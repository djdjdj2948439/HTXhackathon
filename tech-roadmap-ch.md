# Veil Scout：技术路线图与技术栈

**开发周期：** 60 天

---

## 推荐技术栈

### 智能合约（核心）
| 组件 | 工具 | 选型理由 |
|------|------|---------|
| 语言 | **Solidity 0.8.x** | 生态成熟，审计工具最齐全 |
| 框架 | **Foundry (forge + cast)** | 编译快，原生 fuzz 测试，Solidity 原生测试 |
| 本地链 | **Anvil**（Foundry 自带） | 可 fork 主网做集成测试 |
| 部署目标 | **Base (L2)** 或 **Arbitrum Sepolia**（测试网） | Gas 低，出块快 |
| 数学库 | **PRBMath v4**（可选） | 仅 V2 实现 LMSR 时需要；MVP 用简化池子即可 |

### AI 分析师（模块 3）
| 组件 | 工具 | 选型理由 |
|------|------|---------|
| LLM API | **Claude API** 或 **OpenAI GPT-4o** | 项目分析：GitHub、合约、链上数据、里程碑可行性 |
| Agent 脚本 | **Python + web3.py** | 轻量级：读项目数据 → LLM 分析 → 上链设初始赔率 |
| 钱包 | **本地私钥**（仅测试网） | Agent 签名交易，设定初始市场赔率 |
| 数据接入 | **GitHub API + Etherscan API + IPFS 网关** | 获取项目材料用于分析 |

### zkID 防女巫（模块 1）
| 组件 | 工具 | 选型理由 |
|------|------|---------|
| 首选 | **Semaphore v4** | 轻量 ZKP 群组成员证明——nullifierHash 防止每赛季多次领取 |
| 备选 | **Worldcoin IDKit** | 即插即用的唯一人类证明，Semaphore 太复杂时用 |

### 前端
| 组件 | 工具 | 选型理由 |
|------|------|---------|
| 框架 | **Next.js 14** | SSR + API 路由一站式 |
| 样式 | **TailwindCSS + shadcn/ui** | 快速搭建现代 UI |
| 钱包连接 | **RainbowKit + wagmi v2** | 钱包连接体验最佳 |
| 图表 | **Lightweight Charts (TradingView)** | 每个市场的实时赔率图表——视觉冲击力强 |
| 合约交互 | **viem**（wagmi 自带） | 类型安全，速度快 |

### 结算预言机（模块 5）
| 组件 | 工具 | 选型理由 |
|------|------|---------|
| 链上数据 | **Etherscan / Blockscout API** | 读取合约事件，验证里程碑 |
| GitHub 数据 | **GitHub REST API** | 提交活动、PR 合并、部署状态 |
| 预言机脚本 | **Python** | 聚合数据源 → 判定通过/未通过 → 调用 `settle()` 上链 |
| 未来（V2） | **Chainlink Functions / UMA 乐观预言机** | 生产环境去中心化结算 |

---

## 60 天开发路线图

**团队：** 3 人，每人端到端负责一条 Track。

| Track | 范围 | 涉及技术 | 所需技能 |
|-------|------|---------|---------|
| **Track A：合约** | 所有 Solidity 合约 + 测试 + 部署 | Solidity, Foundry, PRBMath | 🔗 合约开发 + 🧮 数学 |
| **Track B：AI + 预言机** | AI 分析师 + 结算预言机 + 数据接入 + Scout Score 设计 | Python, LLM API, web3.py | 🤖 AI/后端 + 🧮 数学 |
| **Track C：前端** | 全部 UI 页面 + 钱包交互 + 图表 | Next.js, React, TailwindCSS, wagmi | 🎨 前端开发 |

---

### ⚠️ Day 0：接口对齐（半天，三人一起）

**唯一的强同步点。** 对齐完接口之后，三人可以完全独立开发 4 周，只需每周日 sync 30 分钟。

#### 需要定义的接口：

**1. 合约 ABI 草案（Track A 产出，Track B/C 消费）**

```solidity
// ScoutCredits.sol
function claimCredits(uint256 seasonId, bytes calldata zkProof) external;
function creditBalance(address user, uint256 seasonId) external view returns (uint256);
event CreditsClaimed(address indexed user, uint256 seasonId, uint256 amount);

// MarketFactory.sol
function createMarket(string calldata milestone, uint256 deadline, string calldata dataSource) external returns (uint256 marketId);
event MarketCreated(uint256 indexed marketId, string milestone, uint256 deadline);

// Market.sol
enum Side { YES, NO }
enum Status { OPEN, TRADING, SETTLING, SETTLED }
function buy(uint256 marketId, Side side, uint256 amount) external;
function getPrice(uint256 marketId) external view returns (uint256 yesPrice, uint256 noPrice);
function getPosition(uint256 marketId, address user) external view returns (uint256 yesAmount, uint256 noAmount);
function seedInitialOdds(uint256 marketId, uint256 yesProbability) external; // AI 调用
event Trade(uint256 indexed marketId, address indexed user, Side side, uint256 amount, uint256 newPrice);

// Settlement.sol
function settle(uint256 marketId, bool passed) external; // 预言机调用
event MarketSettled(uint256 indexed marketId, bool passed);

// Leaderboard.sol
function getScore(address user, uint256 seasonId) external view returns (int256);
function getRanking(uint256 seasonId, uint256 topN) external view returns (address[] memory, int256[] memory);

// RewardVault.sol
function claimReward(uint256 seasonId) external;
event RewardClaimed(address indexed user, uint256 seasonId, uint256 amount);
```

**2. AI 输出 JSON 格式（Track B 产出，Track C 消费）**

```json
{
  "marketId": 1,
  "probability": 0.64,
  "confidence": "medium",
  "bullish": ["Demo 已上线", "合约已部署到主网"],
  "bearish": ["活跃用户少", "无安全审计"],
  "riskFlags": ["疑似刷量交易"],
  "settleable": true,
  "dataSourcesUsed": ["github", "etherscan"]
}
```

**3. 前端需要订阅的事件列表（Track A 产出，Track C 订阅）**

```
CreditsClaimed, MarketCreated, Trade, MarketSettled, RewardClaimed
```

**4. 共享常量**

```
CREDITS_PER_SEASON = 10000       // 每赛季每人积分额度
MAX_CREDIT_PER_MARKET = 2000     // 单市场上限 20%
MIN_PROBABILITY = 0.05
MAX_PROBABILITY = 0.95
```

---

### 独立开发策略：每条 Track 如何不被其他人阻塞

| Track | 依赖谁 | 解除阻塞方案 |
|-------|--------|------------|
| **A：合约** | 不依赖任何人 | 直接开工 |
| **B：AI + 预言机** | 需要合约 ABI + 部署地址 | 前 2 周用本地 Anvil fork 部署 mock 合约（Track A 提供 ABI 即可，不需要完整实现）；也可以先只做 off-chain 部分（数据接入 + LLM 分析），等 Track A 部署后再对接 |
| **C：前端** | 需要合约 ABI + AI 报告 | 前 2 周用 **hardcoded mock 数据** 开发所有页面；ABI 从 Day 0 就有草案；AI 报告用 mock JSON |

**结果：三人 Day 1 开工后可以完全不说话地独立开发 2 周，直到 Week 2 周日 Sync 才需要第一次集成。**

---

### 第一阶段：基础搭建（第 1–14 天）

#### Track A：合约

| 天数 | 任务 |
|------|------|
| 1-2 | 搭建 Foundry 项目 + 项目结构。导出 ABI JSON 文件给 Track B/C 使用（即使合约未完成，ABI 接口已固定） |
| 3-5 | 实现 `ScoutCredits.sol`：不可转让积分代币，按赛季 mint。先用 mock zkID（简单地址白名单） |
| 6-9 | 实现 `Market.sol`：用积分买 YES/NO，单边持仓规则，单市场积分上限，状态机（OPEN → TRADING → SETTLING → SETTLED）。实现简化 AMM 定价 |
| 10-12 | 实现 `MarketFactory.sol`（从里程碑创建市场）+ `Settlement.sol`（owner 触发的通过/未通过，积分重分配给赢家） |
| 13-14 | Foundry 集成测试：创建赛季 → 领取积分 → 创建市场 → 买 YES/NO → 结算 → 验证余额。部署到 Arbitrum Sepolia |

**交付物 A1：** 核心合约部署上测试网 + 导出 ABI 文件。

#### Track B：AI + 预言机

| 天数 | 任务 |
|------|------|
| 1-3 | 搭建 Python 项目。搭建数据接入层：GitHub API（提交、PR、贡献者）、Etherscan API（合约事件、交易统计） |
| 4-7 | 搭建 AI 分析师核心：项目数据 → LLM 提示词 → 结构化 JSON 输出（概率 + 看多/看空理由 + 置信度）。用 Claude 或 GPT-4o |
| 8-10 | 加 sanity check（概率钳制在 0.05–0.95）、LLM 失败回退（默认 0.50）、结构化日志。设计 Scout Score 公式（虚拟 PnL + 准确率 + 早期发现 + 证据 - 惩罚） |
| 11-14 | 用 3-5 个样本项目测试：AI 生成报告 → 验证输出质量。搭建 `seedMarket()` 调用脚本（等 Track A 部署后对接，此阶段可先用本地 Anvil mock） |

**交付物 B1：** 可对任意项目生成分析报告的 AI 分析师 + Scout Score 公式文档。

#### Track C：前端

| 天数 | 任务 |
|------|------|
| 1-3 | 搭建 Next.js 14 + TailwindCSS + shadcn/ui + RainbowKit + wagmi。搭建全局布局、钱包连接、导航栏。创建 `lib/mockData.ts` 提供所有页面的 mock 数据 |
| 4-7 | 搭建赛季入口页面（zkID 验证流程 → 领取积分）。搭建市场浏览页面（市场卡片：项目名、赔率、截止日期、状态） |
| 8-10 | 搭建市场详情页面：赔率显示、买 YES/NO 面板、持仓显示、AI 分析卡片（先读 mock JSON） |
| 11-14 | 搭建 Scout 仪表盘：积分余额、各市场持仓、虚拟 PnL。所有页面用 mock 数据可独立演示 |

**交付物 C1：** 所有核心页面搭建完成（mock 数据），可独立展示 UI 流程。

#### 🔄 第二周周日 Sync（第 14 天）

```
集成内容：
1. Track C 用 Track A 导出的 ABI 替换 mock 数据 → 验证领取积分 + 买 YES/NO 在 UI 上跑通
2. Track B 的 AI 分析师对接 Track A 部署的 MarketFactory → 验证 seedMarket() 能上链
3. 修复接口不匹配的地方
时间：2-3 小时
```

---

### 第二阶段：功能完整（第 15–28 天）

#### Track A：合约

| 天数 | 任务 |
|------|------|
| 15-18 | 集成 Semaphore v4 真实 zkID：用户加入群组 → 生成证明 → 合约验证 nullifier → mint 积分。（Worldcoin IDKit 作为备选） |
| 19-22 | 实现 `Leaderboard.sol`（或链下索引器）：接入 Track B 设计的 Scout Score 公式 |
| 23-25 | 实现 `RewardVault.sol`：赛季奖励池、代币分配给排名前 N 的 Scouts。设计 Alpha Scout SBT 元数据 + mint 功能 |
| 26-28 | 实现证据提交上链：存储每个市场的证据哈希，追踪每个 Scout 的证据分数 |

**交付物 A2：** 完整合约套件：积分 + 市场 + zkID + 排行榜 + 奖励 + 证据。

#### Track B：AI + 预言机

| 天数 | 任务 |
|------|------|
| 15-18 | 搭建结算预言机：截止日读取链上事件 + GitHub API → 聚合数据 → 判定通过/未通过 → 调用 `settle()` 上链 |
| 19-22 | 搭建多数据源验证器：合约事件计数、唯一钱包过滤、GitHub 提交/PR 验证。处理边界情况（数据源宕机 → 重试 / 手动标记） |
| 23-25 | 搭建证据评分助手：AI 读取 Scouts 提交的证据链接 → 评估质量/相关性 → 输出分数建议（MVP 阶段手动确认） |
| 26-28 | 端到端测试：项目截止 → 预言机聚合数据 → 结算市场 → 积分重分配触发 |

**交付物 B2：** 可自动结算市场的结算预言机 + AI 证据评分器。

#### Track C：前端

| 天数 | 任务 |
|------|------|
| 15-18 | 替换所有 mock 数据为真实合约调用。加交易确认流程（加载中 → 成功 → 失败） |
| 19-22 | 搭建证据提交页面：上传链接/截图/分析。搭建 AI 分析报告展示（结构化看多/看空卡片） |
| 23-25 | 搭建排行榜页面：排名表、Scout 个人主页（准确率 %、PnL、早期 Alpha 发现、专长标签）。搭建结算倒计时 + 结果展示 |
| 26-28 | 搭建项目提交页面（项目方提交里程碑）+ 奖励领取页面。全页面打磨 |

**交付物 C2：** 完整功能前端，所有页面对接真实合约。

#### 🔄 第四周周日 Sync（第 28 天）

```
全链路集成测试：
zkID 验证 → 领取积分 → AI 设置市场 → Scout 交易
→ 证据提交 → 截止日 → 预言机结算 → 排行榜更新 → 奖励领取

如果这个流程完整跑通 = 功能完整 ✅
时间：半天
```

---

### 第三阶段：打磨 + 安全（第 29–42 天）

三人回到协作模式，按各自专长分工。

| 天数 | 任务 | 负责人 |
|------|------|--------|
| 29-31 | 合约安全审计：重入攻击、溢出、权限控制。Fuzz 测试积分不可转让性、单边持仓强制、结算边界情况 | Track A 负责人 |
| 29-31 | AI 提示词加固：灌入垃圾项目测试、极端输入测试。预言机重试/失败处理 | Track B 负责人 |
| 29-31 | 响应式设计、错误处理、加载状态、移动端适配 | Track C 负责人 |
| 32-35 | 修复第四周 Sync 发现的集成 bug。压力测试：10+ 市场、20+ Scout 地址 | 全员 |
| 36-38 | 种子演示数据：创建 3-5 个真实项目市场（强/弱/可疑混合）。为每个项目生成 AI 报告 | 全员 |
| 39-42 | UX 打磨：引导流程、工具提示、空状态、交易反馈。合约最终审计 | Track C + Track A |

**交付物：** 生产级 MVP。所有流程顺畅，边界情况处理完毕，演示数据就位。

---

### 第四阶段：演示与答辩（第 43–60 天）

| 天数 | 任务 | 负责人 |
|------|------|--------|
| 43-46 | 编写演示脚本：AI 分析 → Scout 交易 → 证据 → 结算 → 排行榜。排练屏幕操作流程 | 全员 |
| 47-50 | 制作 Pitch Deck：问题 → 解决方案 → 现场演示 → 架构图 → zkID + AI 角色 → 飞轮 → HTX 生态契合度 | 全员（一人主导设计） |
| 51-53 | 撰写机制设计部分：Scout Score 公式推导、积分经济学、防作弊分析（单边规则 + 积分上限 + zkID 如何防作弊） | Track B 负责人 |
| 54-55 | 录制演示视频作为备用方案。准备本地 Anvil 回退方案 | Track C + Track A |
| 56-58 | 排练答辩（目标：5 分钟 pitch + 3 分钟演示 + 2 分钟 Q&A）。准备常见问答："这和投票有什么区别？"、"AI 判断错了怎么办？"、"怎么防串通？" | 全员 |
| 59-60 | 最终 bug 修复，重新部署干净版本，最后一次排练 | 全员 |

**交付物：** 可答辩的项目：现场演示 + 备用视频 + 清晰的"Scout-to-Earn 发现真正的 Builder"叙事。

---

## 关键路径与风险缓解

| 风险 | 概率 | 缓解方案 |
|------|------|---------|
| Semaphore v4 集成复杂度 | 中 | Worldcoin IDKit 作为即插即用备选；最坏情况用简单地址身份 + 频率限制做演示 |
| AI 分析师给出荒谬概率 | 中 | 硬编码回退值（LLM 失败时默认 0.5），概率钳制（0.05–0.95），显示 AI 置信度 |
| 不可转让积分代币边界情况 | 中 | 充分测试：不能转账、不能授权、不能被闪电贷。用自定义实现而非标准 ERC-20 |
| 结算预言机数据不可靠 | 中 | 每个市场支持多数据源。演示时使用预设的可验证数据 |
| Scout Score 博弈（全部押一个市场） | 低 | 单市场积分上限（最高 20%）。Score 公式中加过度集中的风险惩罚 |
| 演示日现场链问题 | 中 | 预录演示视频作为备用，部署到本地 Anvil 作为第二备用方案 |

---

## 建议文件结构

```
veil-scout/
├── contracts/                  # Foundry 项目
│   ├── src/
│   │   ├── ScoutCredits.sol   # 不可转让积分代币（灵魂绑定）
│   │   ├── Season.sol         # 赛季生命周期 + zkID nullifier 注册表
│   │   ├── Market.sol         # YES/NO 市场：买入、卖出、持仓追踪
│   │   ├── MarketFactory.sol  # 从项目里程碑创建市场
│   │   ├── Settlement.sol     # 预言机触发的通过/未通过 + 积分重分配
│   │   ├── Leaderboard.sol    # Scout Score 计算 + 排名（或链下索引器）
│   │   └── RewardVault.sol    # 赛季奖励池 + 代币分配
│   ├── test/
│   │   ├── ScoutCredits.t.sol # 不可转让性、mint 门控、赛季限制
│   │   ├── Market.t.sol       # 单边规则、积分上限、状态机
│   │   └── Integration.t.sol  # 完整赛季生命周期
│   └── foundry.toml
├── ai-analyst/                 # Python AI 分析师
│   ├── analyst.py             # 主流程：监听新项目 → 分析 → 设置赔率
│   ├── llm.py                 # LLM API 封装（项目数据 → 概率 + 报告）
│   ├── data_ingestion.py      # 获取 GitHub / Etherscan / IPFS 数据
│   └── requirements.txt
├── oracle/                     # 结算预言机
│   ├── verifier.py            # 聚合数据源 → 通过/未通过
│   ├── sources/               # 数据源适配器（etherscan、github、自定义 API）
│   └── settler.py             # 上链发布结果
├── frontend/                   # Next.js 应用
│   ├── app/
│   │   ├── page.tsx           # 落地页："Scout-to-Earn：发现真正的 Builder"
│   │   ├── season/            # 赛季入口 + zkID 验证
│   │   ├── markets/           # 浏览所有项目里程碑市场
│   │   ├── market/[id]/       # 市场详情：赔率图表、交易面板、AI 报告、证据
│   │   ├── submit/            # 项目方：提交里程碑以创建市场
│   │   ├── leaderboard/       # Scout 排名、分数、个人主页
│   │   └── dashboard/         # Scout：积分余额、持仓、PnL、奖励
│   ├── components/
│   ├── lib/
│   │   ├── contracts.ts       # ABI + 地址
│   │   └── wagmi.ts           # 钱包配置
│   └── package.json
└── docs/
    ├── The Oracle of Truth.md  # 项目设计文档（Veil Scout）
    └── tech-roadmap.md         # 本文件
```
