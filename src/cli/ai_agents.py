#!/usr/bin/env python3
"""CLI wrappers for AI coding agents (Qwen, DeepSeek) integration."""

import asyncio
import json
import subprocess
from pathlib import Path

import click
import httpx


class QwenAgent:
    """Qwen Coder agent via Ollama."""

    def __init__(self, model: str = "qwen2.5-coder:7b"):
        self.model = model
        self.base_url = "http://localhost:11434"

    async def generate_code(self, prompt: str, context: str | None = None) -> str:
        """Generate code using Qwen Coder."""
        full_prompt = f"{context}\n\n{prompt}" if context else prompt

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": full_prompt,
                        "stream": False
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                result = response.json()
                return result.get("response", "")
        except (httpx.HTTPError, json.JSONDecodeError) as e:
            return f"Error: {e}"

    async def analyze_code(self, code: str, task: str) -> str:
        """Analyze existing code."""
        prompt = f"""
        Task: {task}
        Please analyze this code:
        ```
        {code}
        ```
        Provide specific suggestions and improvements.
        """
        return await self.generate_code(prompt)


class DeepSeekAgent:
    """DeepSeek Coder agent via Ollama or API."""

    def __init__(self, model: str = "deepseek-coder:6.7b", use_api: bool = False):
        self.model = model
        self.use_api = use_api
        self.base_url = "http://localhost:11434" if not use_api else "https://api.deepseek.com/v1"

    async def generate_code(self, prompt: str, context: str | None = None) -> str:
        """Generate code using DeepSeek Coder."""
        if self.use_api:
            return await self._api_generate(prompt, context)
        return await self._ollama_generate(prompt, context)

    async def _ollama_generate(self, prompt: str, context: str | None = None) -> str:
        """Generate via local Ollama."""
        full_prompt = f"{context}\n\n{prompt}" if context else prompt

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": full_prompt,
                        "stream": False
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                result = response.json()
                return result.get("response", "")
        except (httpx.HTTPError, json.JSONDecodeError) as e:
            return f"Error: {e}"

    async def _api_generate(self, prompt: str, context: str | None = None) -> str:
        """Generate via DeepSeek API."""
        # Implementation would use DeepSeek API key
        # For now, fallback to Ollama
        return await self._ollama_generate(prompt, context)


@click.group()
def ai_agents():
    """AI coding agents CLI."""


@ai_agents.command()
@click.argument('prompt')
@click.option('--file', '-f', help='File to use as context')
@click.option('--model', '-m', default='qwen2.5-coder:7b', help='Qwen model to use')
def qwen(prompt: str, file: str | None, model: str):
    """Generate code using Qwen Coder."""
    async def _qwen():
        agent = QwenAgent(model)

        context = None
        if file and Path(file).exists():
            context = Path(file).read_text()

        result = await agent.generate_code(prompt, context)
        click.echo(result)

    asyncio.run(_qwen())


@ai_agents.command()
@click.argument('prompt')
@click.option('--file', '-f', help='File to use as context')
@click.option('--model', '-m', default='deepseek-coder:6.7b', help='DeepSeek model to use')
@click.option('--api', is_flag=True, help='Use DeepSeek API instead of local Ollama')
def deepseek(prompt: str, file: str | None, model: str, api: bool):
    """Generate code using DeepSeek Coder."""
    async def _deepseek():
        agent = DeepSeekAgent(model, api)

        context = None
        if file and Path(file).exists():
            context = Path(file).read_text()

        result = await agent.generate_code(prompt, context)
        click.echo(result)

    asyncio.run(_deepseek())


@ai_agents.command()
@click.argument('file_path')
@click.argument('task')
@click.option('--agent', '-a', type=click.Choice(['qwen', 'deepseek']), default='qwen', help='AI agent to use')
def analyze(file_path: str, task: str, agent: str):
    """Analyze code file with specified AI agent."""
    async def _analyze():
        if not Path(file_path).exists():
            click.echo(f"File not found: {file_path}")
            return

        code = Path(file_path).read_text()

        if agent == 'qwen':
            ai_agent = QwenAgent()
            result = await ai_agent.analyze_code(code, task)
        else:
            ai_agent = DeepSeekAgent()
            result = await ai_agent.generate_code(f"Analyze this code for: {task}\n\n```\n{code}\n```")

        click.echo(result)

    asyncio.run(_analyze())


@ai_agents.command()
def install_models():
    """Install recommended AI models via Ollama."""
    models = [
        "qwen2.5-coder:7b",
        "qwen2.5-coder:1.5b",
        "deepseek-coder:6.7b",
        "deepseek-coder:1.3b"
    ]

    click.echo("Installing AI coding models...")
    for model in models:
        click.echo(f"Installing {model}...")
        try:
            subprocess.run(["ollama", "pull", model], check=True)
            click.echo(f"✓ {model} installed")
        except subprocess.CalledProcessError:
            click.echo(f"✗ Failed to install {model}")


if __name__ == '__main__':
    ai_agents()
