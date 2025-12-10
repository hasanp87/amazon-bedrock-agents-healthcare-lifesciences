from .context import TemplateContext
from .memory_hook_provider import MemoryHook
from .utils import get_ssm_parameter
from .agent import DynamicSOPAgent
from bedrock_agentcore.memory import MemoryClient
import logging
from pathlib import Path

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

memory_client = MemoryClient()


async def agent_task(user_message: str, session_id: str, actor_id: str):
    agent = TemplateContext.get_agent_ctx()

    response_queue = TemplateContext.get_response_queue_ctx()
    gateway_access_token = TemplateContext.get_gateway_token_ctx()

    if not gateway_access_token:
        raise RuntimeError("Gateway Access token is none")
    try:
        if agent is None:
            # Create memory hook (using a default memory_id for now)
            memory_hook = MemoryHook(
                memory_client=memory_client,
                memory_id=get_ssm_parameter("/app/myapp/agentcore/memory_id"),
                actor_id=actor_id,
                session_id=session_id,
            )

            # Determine SOP directories
            sop_dirs = []
            examples_dir = Path(__file__).parent.parent.parent / "examples" / "sops"
            if examples_dir.exists():
                sop_dirs.append(str(examples_dir))

            agent = DynamicSOPAgent(
                bearer_token=gateway_access_token,
                memory_hook=memory_hook,
                sop_directories=sop_dirs,
            )

            TemplateContext.set_agent_ctx(agent)

        async for chunk in agent.stream(user_query=user_message):
            await response_queue.put(chunk)

    except Exception as e:
        logger.exception("Agent execution failed.")
        await response_queue.put(f"Error: {str(e)}")
    finally:
        await response_queue.finish()
