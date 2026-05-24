# AGENTS

This file is for AI agents (Hermes, Claude Code, Codex) working in this project.

## Project Overview

团险报价助手 - 为企业客户提供快速保费计算、方案模板和风控建议的 Web 应用。

## Build Commands

TBD - depends on chosen tech stack

## Architecture

TBD

## Security Baseline

- 客户数据加密存储
- 不存储敏感个人信息（身份证号、手机号等）
- API 访问限流
- 输入校验防止注入攻击

## Engine Guidance

- Complex multi-file changes, new features → Claude Code
- Quick targeted fixes, single-file changes → Codex
- Deploy, monitor, notify, schedule → Hermes
- UI/UX exploration before coding → Claude Design (human step)
- Not sure? Tell Hermes: run choose-engine

## Monitoring

- Health endpoint: /api/health
- Error tracking: TBD

## Deployment

- Platform: TBD
- Production: main branch → automatic deploy

## Commit Conventions

- One commit per meaningful change
- Never commit .env or credentials
