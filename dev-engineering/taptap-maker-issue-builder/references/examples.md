# Examples and anti-patterns

## Good pattern: concise issue escalation

Raw context: user complaint about duplicated payment for a paid game/service, with transaction IDs and amount.

Good output:

```markdown
[一句话问题 / 需要协助]：@陈一豪(cyh) 用户在 TapTap 购买「全面憨憨战争模拟器」时出现重复付款，请协助确认两笔交易归属，并判断正常退款路径是否可直接处理。

【用户问题】：支付 18 元成功后未获得服务，用户又重新支付一笔。
【用户诉求】：联系自己并退款。
【交易号】：2026041122001497031406254326、2026041122001497031406304454
【外部交易号】：69da248b2df5595d36026、69da25902df5595d375c3
【总金额】：36
【商品 / 服务名称】：全面憨憨战争模拟器
【商家名称 + ID】：2088221893002276 易玩上海网络科技有限公司
【已查证】：一笔为兑换码（买给他人），一笔为直接购买。
【待确认】：是否需要用户授权联系方式；退款是否走正常渠道追退。
```

Why it works:

- The first line states the issue and the requested action.
- Transaction evidence is grouped and exact.
- The reader can decide next steps without reading the raw thread.

## Good pattern: AI experiment / collaboration request

Raw context: user wants to do an AB experiment on Claude Code error rate when context is high, has run a first experiment with weak signal, and suspects the scaffold task is too simple.

Good output:

```markdown
[一句话问题 / 需要协助]：建议先 @林美辰 看 AI 实验设计，cc @赵天一 看任务构造方向：我想验证「上下文占比过高时 Claude Code 是否更容易犯错」以及「>50% 上下文后插入 hook 是否能降低犯错率」，但当前实验信号不明显，需要协助构造一个稳定高频、可复现的 TapTap Maker 游戏任务样本。

【目标】：验证上下文占比过高与 Claude Code 犯错率之间的关系，并评估插入 hook 后是否能降低犯错率。
【当前方案】：构建任务脚手架，让 Claude Code 在脚手架上执行任务；当上下文占比达到 50% 以上时，每轮对话插入 hook，对比犯错率变化。
【已做实验 / 结果】：已跑过一版实验，但效果没有达到预期，信号不明显。
【当前判断】：可能是脚手架任务过于简单，AI 不容易稳定犯错，导致实验无法拉开差异。
【需要协助】：
1. 判断 TapTap Maker 里是否有适合构造的高频失败场景。
2. 设计一个小型游戏任务，让 AI 在上下文变长后更容易稳定出错。
3. 提供历史上高频、可复现、错误可判定的问题样本，方便接入当前 AB 实验流程。
【理想样本 / 验收标准】：可重复执行、错误可判定、难度适中、上下文累积后更容易出错。
【待确认】：是否要拉具体游戏 owner 一起构造样本，例如 puzzle / story / card / simulation 方向。
```

Why it works:

- It frames the request as an experiment-design and dataset-construction problem, not a confirmed product bug.
- It separates objective, current approach, observed result, hypothesis, requested help, and acceptance criteria.
- It routes to AI/tool methodology first, while leaving room for product/game owners.

## Bad pattern: broad map used as an issue report

Do not answer a specific operational problem with a large all-scenario taxonomy such as `10 大类问题 / 70+ 去重问题 / 优先级建议 / 后续落地建议`. This is useful for retrospectives or knowledge mapping, not for quickly resolving a concrete Slack issue.

Problems with this pattern:

- No single owner or required action is obvious.
- The reader must infer the actual blocker.
- It mixes unrelated categories and hides the immediate evidence.
- It is high effort for the reader and low utility for triage.

## Bad pattern: unfiltered chat transcript

Do not paste a multi-person internal thinking trail directly into Slack when asking for help. Raw discussion such as `我觉得可能是... / 对的... / 我想想...` can be useful as source context, but the final issue report should convert it into objective fields:

- `【目标】`
- `【当前方案】`
- `【已做实验 / 结果】`
- `【当前判断】`
- `【需要协助】`
- `【待确认】`

## Rewrite rules

When raw input contains a long narrative, rewrite it by asking:

1. What is the concrete thing that is broken, ambiguous, or being decided?
2. Who can unblock it fastest?
3. What exact action is requested?
4. Which IDs, logs, screenshots, timestamps, states, prior checks, experiment results, or model names prove the issue?
5. What is still unknown?

Then output only the answer to those questions.
