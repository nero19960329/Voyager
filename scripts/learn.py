import argparse

from voyager import Voyager
from voyager.memory import AgentMemoryMode


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--azure-client-id", type=str, required=True)
    parser.add_argument("--azure-secret-value", type=str, required=True)
    parser.add_argument("--openai-api-key", type=str, required=True)
    parser.add_argument("--env-request-timeout", type=int, default=600)
    parser.add_argument("--max-iterations", type=int, default=160)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--agent_memory_mode", type=AgentMemoryMode, choices=list(AgentMemoryMode), default=AgentMemoryMode.AGENT_MEMORY_MODE_NONE)
    parser.add_argument("--action-agent-temperature", type=float, default=0.0)
    parser.add_argument("--curriculum-agent-temperature", type=float, default=0.0)
    parser.add_argument("--curriculum-agent-qa-temperature", type=float, default=0.0)
    parser.add_argument("--critic-agent-temperature", type=float, default=0.0)
    parser.add_argument("--skill-manager-temperature", type=float, default=0.0)
    args = parser.parse_args()

    azure_login = {
        "client_id": args.azure_client_id,
        "redirect_url": "https://127.0.0.1/auth-response",
        "secret_value": args.azure_secret_value,
        "version": "fabric-loader-0.14.18-1.19", # the version Voyager is tested on
    }
    openai_api_key = args.openai_api_key

    voyager = Voyager(
        azure_login=azure_login,
        openai_api_key=openai_api_key,
        env_request_timeout=args.env_request_timeout,
        max_iterations=args.max_iterations,
        action_agent_temperature=args.action_agent_temperature,
        curriculum_agent_temperature=args.curriculum_agent_temperature,
        curriculum_agent_qa_temperature=args.curriculum_agent_qa_temperature,
        critic_agent_temperature=args.critic_agent_temperature,
        skill_manager_temperature=args.skill_manager_temperature,
        resume=args.resume,
        agent_memory_mode=args.agent_memory_mode,
    )

    # start lifelong learning
    voyager.learn()
