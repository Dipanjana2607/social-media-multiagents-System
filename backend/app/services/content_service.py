from app.agents.planner_agent import PlannerAgent
from app.agents.executor_agent import ExecutorAgent
from app.agents.verifier_agent import VerifierAgent
from app.prompts.prompt_registry import get_prompt  
from app.dtos.request_dtos import GenerateContentRequest
from app.dtos.response_dtos import GenerateContentResponse, AgentStepResult
from app.utils.logger import get_logger

logger = get_logger("services.content_service")


class ContentService:
    def __init__(self):
        # align attribute names with usage in methods
        self.planner = PlannerAgent()
        self.executor = ExecutorAgent()
        self.verifier = VerifierAgent()

    def generate(self, request: GenerateContentRequest) -> GenerateContentResponse:
        """Compatibility wrapper used by the controller (calls generate_content)."""
        return self.generate_content(request)

    def generate_content(self, request: GenerateContentRequest) -> GenerateContentResponse:
        logger.info(f"generate_content start: platform={request.platform} topic={request.topic} max_retries={request.max_retries}")
        platform_prompts = get_prompt(request.platform)
        planner_prompts = platform_prompts["planner"]
        executor_prompts = platform_prompts["executor"]
        verifier_prompts = platform_prompts["verifier"]

        steps: list = []
        
        attempt = 0

        max_retries = request.max_retries

        content = ""
        plan = ""

        # ── Step 3: The retry loop ─────────────────────────────────────────────
        # "while condition:" keeps repeating the block as long as condition is True.
        # We stop when attempt reaches max_retries OR when verifier says PASS.
        while attempt < max_retries:

            # Increment first — so attempt starts at 1 (not 0) in our records.
            # "+= 1" is shorthand for "attempt = attempt + 1"
            attempt += 1

            # ── 3a: Run the PLANNER ───────────────────────────────────────────
            # Pass the platform-specific prompt config + user's request data.
            # The PlannerAgent fills in {topic}, {tone}, {extra} placeholders.
            plan = self.planner.run(
                prompt_config=planner_prompts,
                topic=request.topic,
                tone=request.tone,
                # "or ''" converts None to empty string if extra is None.
                extra=request.extra or "",
            )

            # Record this step.
            # .title() capitalizes first letter: "linkedin" → "LinkedIn"
            steps.append(AgentStepResult(
                agent_name=f"{request.platform.title()} Planner",
                output=plan,
                attempts=attempt,
            ))

            # ── 3b: Run the EXECUTOR ──────────────────────────────────────────
            # Pass the plan (planner's output) into the executor.
            # This is how agents communicate — the output of one becomes input to next.
            content = self.executor.run(
                prompt_config=executor_prompts,
                plan=plan,
                topic=request.topic,
                tone=request.tone,
            )

            steps.append(AgentStepResult(
                agent_name=f"{request.platform.title()} Executor",
                output=content,
                attempts=attempt,
            ))

            passed, verdict = self.verifier.run(
                prompt_config=verifier_prompts,
                content=content,
                plan=plan,
                topic=request.topic,
            )

            steps.append(AgentStepResult(
                agent_name=f"{request.platform.title()} Verifier",
                output=verdict,
                attempts=attempt,
            ))

            if passed:
                return GenerateContentResponse(
                    platform=request.platform,
                    topic=request.topic,
                    tone=request.tone,
                    final_content=content,
                    agent_steps=steps,
                    total_attempts=attempt,
                    success=True,
                )
            
            if self.verifier.wants_full_restart(verdict):
                # "continue" skips the rest of the loop body and goes back to top.
                continue

            # If verifier only wants executor to retry (RESTART_STAGE: EXECUTOR),
            # we do a cheaper retry: keep the plan, just re-run the executor
            # with the verifier's feedback appended so it knows what to fix.
            if attempt < max_retries:
                feedback = self.verifier.extract_feedback(verdict)

                # Inject the feedback into the plan string.
                # The executor will see both the original plan AND the feedback.
                enriched_plan = (
                    plan
                    + "\n\n--- VERIFIER FEEDBACK (fix these issues) ---\n"
                    + feedback
                )

                # Re-run just the executor with the enriched plan.
                content = self.executor.run(
                    prompt_config=executor_prompts,
                    plan=enriched_plan,
                    topic=request.topic,
                    tone=request.tone,
                )

                steps.append(AgentStepResult(
                    agent_name=f"{request.platform.title()} Executor (retry)",
                    output=content,
                    attempts=attempt,
                ))

                # Verify the retried content.
                passed, verdict = self.verifier.run(
                    prompt_config=verifier_prompts,
                    content=content,
                    plan=plan,
                    topic=request.topic,
                )

                steps.append(AgentStepResult(
                    agent_name=f"{request.platform.title()} Verifier (retry)",
                    output=verdict,
                    attempts=attempt,
                ))

                # If the retry passed, return success.
                if passed:
                    return GenerateContentResponse(
                        platform=request.platform,
                        topic=request.topic,
                        tone=request.tone,
                        final_content=content,
                        agent_steps=steps,
                        total_attempts=attempt,
                        success=True,
                    )

        # ── Step 4: Max retries exhausted ─────────────────────────────────────
        # We exit the while loop because attempt == max_retries.
        # Return the best content we have, even though it didn't pass verification.
        logger.info(f"generate_content finished: attempts={attempt} success=False")
        return GenerateContentResponse(
            platform=request.platform,
            topic=request.topic,
            tone=request.tone,
            final_content=content,
            agent_steps=steps,
            total_attempts=attempt,
            success=False,
        )


