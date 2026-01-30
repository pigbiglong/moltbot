# 桌面宠物功能设计文档

**项目**: Moltbot
**日期**: 2025-01-30
**版本**: 1.0

## 概述

创建一个交互式桌面宠物，集成到 macOS App 中，提供：

- **工作/休闲状态显示**：基于任务队列自动切换
- **语音和点击唤醒**：使用现有 Voice Wake + 点击手势
- **任务监控面板**：快速查看运行中/等待中的任务
- **不打扰设计**：固定在屏幕边缘，不遮挡工作区

---

## 第一节：整体架构与核心组件

### 架构概述

桌面宠物系统作为 macOS App 的新模块，复用现有的 `VoiceWakeRuntime` 和任务队列基础设施。

**核心组件**：

#### 1. PetManager (Swift Actor)
- 单例实例管理宠物生命周期
- 监听 Gateway WebSocket 的任务事件（`jobs.changed`、`jobs.started`、`jobs.completed`）
- 维护宠物状态和任务队列快照
- 处理唤醒事件（点击和 Voice Wake 触发）
- 管理 NSWindow 实现和动画循环

#### 2. PetWindowController
- 创建和管理屏幕边缘的浮动窗口（NSPanel 样式）
- 支持 4 个角落位置（左上/右上/左下/右下）
- 通过 UserDefaults 持久化位置偏好
- 窗口背景透明，无标题栏，点击穿透到下方桌面
- 窗口层保持在菜单栏之下，普通窗口之上

#### 3. PetRenderer
- 渲染当前宠物视觉（默认简单图标动画）
- 插件系统支持加载自定义宠物包（2D Sprite 或 3D 模型）
- 状态动画：
  - 呼吸（idle）
  - 眨眼（idle 间歇）
  - 快速动画（working）
  - 摇晃（error）
- 性能优化：使用 CADisplayLink 或 Timer 控制帧率（15 FPS）

#### 4. PetInteractionHandler
- 处理鼠标点击事件（`gestureRecognizer`）
- 监听 Voice Wake 唤醒事件（需要特定唤醒词前缀，如 "Pet show"）
- 触发时显示上下文菜单：
  - "任务监控"
  - "状态详情"
  - "切换宠物"
  - "设置"

#### 5. TaskMonitorController
- 订阅 Gateway 的 `jobs.list` RPC 方法
- 监听实时推送事件（`job.started`、`job.completed`、`job.failed`）
- 维护任务计数：`runningCount`、`waitingCount`、`errorCount`
- 当任何计数变化时通知 `PetManager` 更新状态

---

## 第二节：状态管理与数据流

### PetState 定义

```swift
enum PetState {
    case idle                          // 无任务运行，宠物休息
    case working                       // 有任务执行中
    case processing(jobId: String)       // 具体任务处理中（可选显示进度）
    case waiting(count: Int)            // 等待队列中的任务
    case error(message: String)          // 最近任务失败
    case disconnected                  // Gateway 连接断开
}

struct PetContext {
    let state: PetState
    let runningTasks: [JobInfo]
    let waitingTasks: [JobInfo]
    let lastError: JobError?
    let uptime: TimeInterval
}
```

### 数据流

#### 1. Gateway → TaskMonitor → PetManager

**WebSocket 事件流**：
- `job.started` → `PetContext` 增加到 `runningTasks`
- `job.completed` → 从 `runningTasks` 移除
- `job.failed` → 移到 `runningTasks`，设置 `lastError`，切换 `state` 为 `.error`
- `jobs.list` 响应 → 全量同步任务队列，更新 `runningCount` 和 `waitingCount`

#### 2. PetContext → PetRenderer

- 状态变化触发动画切换（如 working → idle）
- 显示任务计数徽章（如等待 3、运行 1）
- 错误状态显示特殊视觉提示（摇晃、红色边框）

#### 3. PetManager → Gateway (交互)

- 用户点击宠物 → 调用 `GatewayClient.request("jobs.list")` 打开监控面板
- 语音唤醒 "Pet show" → 触发 `PetWindowController.showMenu()`
- 菜单选择 "切换宠物" → 调用 `PetManager.nextPet()`

### 状态转换规则

```
初始: idle
├─ runningTasks > 0 → working
├─ lastError ≠ nil → error
└─ 等待队列更新 → waiting(count)

working:
├─ runningTasks == 0 → idle
├─ 任务失败 → error
└─ 保持 working 直到所有任务完成

error:
├─ 3秒后自动 → idle（超时重置）
└─ 用户点击宠物 → 显示错误详情菜单

waiting:
└─ 任务开始执行 → working

disconnected:
├─ WebSocket 重连 → 恢复之前状态
└─ 超过重试上限 → 保持 disconnected
```

### 持久化

- **窗口位置**：`UserDefaults(key: "pet.windowPosition")`，枚举值：`.topLeft/.topRight/.bottomLeft/.bottomRight`
- **当前宠物类型**：`UserDefaults(key: "pet.currentType")`，字符串 ID
- **唤醒词前缀**：`UserDefaults(key: "pet.wakeWordPrefix")`，默认 "Pet"

---

## 第三节：UI 设计与交互

### PetWindow 布局

#### 1. 浮动窗口

- **尺寸**：80x80pt（默认图标），可扩展到 120x120pt（2D/3D 角色）
- **样式**：`NSPanel`, `level: .floating`, `styleMask: .borderless`
- **背景**：完全透明，仅渲染宠物内容
- **点击行为**：整个窗口可点击，触发手势识别

#### 2. 位置管理

- 支持 4 个预设角：
  - `.topLeft`
  - `.topRight`
  - `.bottomLeft`
  - `.bottomRight`
- **默认**：`.bottomRight`（不打扰常用工作区）
- **屏幕边缘留白**：20pt 边距
- **拖动**：Shift+拖动临时移动，松开后自动对齐到最近的角

#### 3. 上下文菜单

点击宠物时弹出 NSMenu，位于宠物下方：

```
查看任务...            [Cmd+Shift+P]
━━━━━━━━━━━━━━━━━━
状态：Working (2 运行中)
━━━━━━━━━━━━━━━━━━
切换宠物              [Cmd+Shift+N]
设置...
```

**菜单项**：
- "查看任务..." → 打开 Jobs 窗口
- "状态：Working (2 运行中)" → 信息条目（不可点）
- "-" → 分隔符
- "切换宠物" → 循环到下一个可用宠物
- "设置..." → 打开宠物偏好设置

**键盘快捷键**：
- `Cmd+Shift+P`：显示任务监控面板
- `Cmd+Shift+N`：切换到下一个宠物

### 视觉反馈

#### 1. 状态指示

| 状态 | 动画 | 持续时间 |
|------|-------|-----------|
| **Idle** | 平静呼吸（透明度 0.7-1.0） | 2秒周期 |
| **Working** | 快速弹跳/点头（scale 0.95-1.05） | 0.5秒周期 |
| **Waiting** | 摇尾巴/晃动（rotation ±5°） | 1秒周期 |
| **Error** | 红色边框闪烁 + 摇头（rotation ±10°） | 0.8秒周期 |
| **Disconnected** | 半透明灰色（opacity 0.5） | 静态 |

#### 2. 任务徽章

- **触发条件**：工作状态时显示
- **位置**：宠物右上方，10pt 圆形背景
- **多重状态徽章**：
  - 左上角：运行中（绿色，count = runningCount）
  - 右上角：等待中（黄色，count = waitingCount）
- **空值处理**：count = 0 时不显示对应徽章

#### 3. 唤醒响应

- **Voice Wake 触发**：宠物旋转一圈（360°）+ 弹出气泡 "Hi!"
- **点击触发**：缩放动画（scale 1.0 → 1.2 → 1.0，持续 200ms）
- **错误气泡**：3 秒自动消失

### 动画系统

使用 `CAAnimation` 或 `CALayer` 实现平滑过渡：

```swift
// 基础呼吸动画
let breatheAnimation = CABasicAnimation(keyPath: "opacity")
breatheAnimation.fromValue = 0.7
breatheAnimation.toValue = 1.0
breatheAnimation.duration = 1.0
breatheAnimation.autoreverses = true
breatheAnimation.repeatCount = .infinity
petLayer.add(breatheAnimation)

// 状态切换过渡
CATransaction.begin()
CATransaction.setAnimationDuration(0.3)
petLayer.opacity = newState == .idle ? 1.0 : 0.8
petLayer.transform = newState == .working ?
    CATransform3DMakeScale(1.1, 1.1, 1.0) :
    CATransform3DIdentity
CATransaction.commit()
```

---

## 第四节：错误处理、测试与扩展性

### 错误处理

#### 1. 通信错误

| 场景 | 处理方式 |
|------|---------|
| Gateway WebSocket 断开 | 宠物进入 `.disconnected` 状态（灰色、半透明） |
| RPC 请求失败（如 `jobs.list`） | 显示错误气泡 3 秒，然后回到之前状态 |
| 重连失败 | 每 5 秒重试，最多 3 次，进入离线模式 |

#### 2. 渲染错误

| 场景 | 处理方式 |
|------|---------|
| 宠物包加载失败 | 回退到默认系统图标（SF Symbols） |
| 动画卡死 | 超过 30 秒无响应则停止动画循环，记录错误 |
| 窗口创建失败 | 尝试 3 次，每次位置向内偏移 50pt |

#### 3. 用户输入错误

- **Voice Wake 误触发**：0.5 秒的"拒绝"动画（摇头）
- **点击过于频繁**（< 100ms 间隔）：忽略，防止误触

### 测试策略

#### 1. 单元测试（Vitest - UI 逻辑）

```typescript
// PetManager 逻辑测试
describe("PetManager", () => {
    test("idle → working when task starts")
    test("working → idle when all tasks complete")
    test("error state clears after timeout")
    test("task count updates correctly")
    test("badge numbers match queue state")
})
```

#### 2. 集成测试（Swift）

```swift
// PetWindowController 测试
class PetWindowControllerTests {
    test("window renders at correct corner position")
    test("click triggers menu display")
    test("drag and snap to corner works")
    test("keyboard shortcuts work")
}

// Gateway 事件模拟
class PetGatewayIntegrationTests {
    test("job.started event updates pet state")
    test("multiple jobs update badge correctly")
    test("error state persists until cleared")
}
```

#### 3. E2E 测试

测试流程：
1. 启动 App → 创建宠物窗口 → 位置正确
2. 模拟 Gateway 事件 → 状态变化正确
3. Voice Wake 触发 → 菜单显示 → 点击"查看任务" → Jobs 窗口打开
4. 切换宠物 → 视觉立即更新
5. 拖动宠物到新位置 → 松开后自动对齐到角

### 扩展性设计

#### 1. 宠物包插件系统

```swift
protocol PetPackage {
    var id: String { get }
    var name: String { get }
    var type: PetType { get } // .icon / .sprite2D / .model3D
    func render(in context: CGContext, state: PetState) throws
    func idleAnimation() throws -> AnimationSequence
    func workingAnimation() throws -> AnimationSequence
}

enum PetType {
    case icon        // SF Symbols / 图片
    case sprite2D     // Sprite Sheet + JSON
    case model3D      // 3D 模型文件
}
```

**包位置**：`~/.moltbot/pets/`

**内置宠物**：
- `DefaultIconPet`：系统图标
- `BouncingBallPet`：简单弹跳动画
- `CatSpritePet`：2D 精灵图角色

**用户安装**：从 GitHub 或本目录加载 `.moltbot-pet` 扩展

#### 2. 自定义动画

- **JSON 配置**：定义关键帧动画
- **Lottie 支持**：`.lottie` 文件直接渲染
- **Sprite Sheet**：`.png` + `.json` 帧序列

#### 3. 事件钩子系统

用户可以注册自定义回调：
```swift
protocol PetEventHook {
    func onPetClicked(state: PetState)
    func onStateChanged(from: PetState, to: PetState)
    func onTaskCompleted(job: JobInfo)
}
```

通过 Extension API 暴露给第三方开发者。

---

## 开发路径

### 第一阶段：核心实现
1. 创建 `PetManager` Actor 和基础状态机
2. 实现 `PetWindowController`（NSPanel）
3. 集成 `TaskMonitorController` 与 Gateway
4. 基础渲染（系统图标 + 状态徽章）

### 第二阶段：交互与动画
1. 实现点击手势和上下文菜单
2. Voice Wake 集成（唤醒词前缀）
3. 状态切换动画（呼吸/弹跳/摇晃）
4. 窗口位置持久化和拖动

### 第三阶段：扩展系统
1. 设计并实现 `PetPackage` 协议
2. 创建第一个扩展宠物（2D Sprite）
3. 文档化 API 和包格式
4. 包管理器 UI（安装/卸载/切换）

### 第四阶段：测试与优化
1. 完善单元测试覆盖
2. 性能优化（帧率控制、内存使用）
3. 错误处理完善
4. 文档编写

---

## 待确认问题

1. **宠物大小限制**：是否支持用户调整大小？
2. **徽章显示阈值**：多少任务时开始显示徽章（如 >= 1）？
3. **错误状态持续**：错误状态下宠物是否保持错误显示直到用户手动清除？
4. **宠物包分发**：是否需要官方宠物仓库？
5. **性能要求**：动画帧率上限（15 FPS / 30 FPS / 60 FPS）？

---

## 参考文件

### 新增文件

```
apps/macos/Sources/Moltbot/Pet/
├── PetManager.swift              # 核心状态管理 Actor
├── PetWindowController.swift     # 窗口和位置管理
├── PetRenderer.swift            # 渲染引擎和动画
├── PetInteractionHandler.swift   # 点击和 Voice Wake 处理
├── PetState.swift              # 状态定义和转换逻辑
├── PetConstants.swift           # 配置常量
└── PetPackageProtocol.swift      # 扩展协议

apps/macos/Sources/Moltbot/Pet/Packages/
└── DefaultIconPet.swift         # 内置默认宠物

apps/macos/Sources/Moltbot/Pet/Extensions/
└── PetExtensionManager.swift     # 包管理和加载

apps/macos/Sources/Moltbot/MenuBar.swift
└── [修改] 添加宠物启用开关

apps/macos/Sources/Moltbot/AppState.swift
└── [修改] 添加宠物相关状态

apps/macos/Tests/MoltbotIPCTests/
├── PetManagerTests.swift        # 单元测试
├── PetWindowControllerTests.swift
└── PetGatewayIntegrationTests.swift
```

### 修改现有文件

```
apps/macos/Sources/Moltbot/VoiceWakeRuntime.swift
└── [修改] 暴露唤醒事件给宠物系统

apps/macos/Sources/Moltbot/GatewayConnection.swift
└── [修改] 添加 jobs.* 事件监听路由

apps/macos/Sources/Moltbot/MenuContentView.swift
└── [修改] 集成宠物设置入口
```

---

## 总结

本设计描述了一个完整的桌面宠物系统，包括：

✅ **架构**：PetManager + PetWindowController + TaskMonitor + PetRenderer + PetInteractionHandler
✅ **状态管理**：6 种状态（idle/working/processing/waiting/error/disconnected）+ 实时任务队列同步
✅ **UI 设计**：屏幕边缘浮动、4 个角落位置、上下文菜单、任务徽章
✅ **交互**：点击 + Voice Wake 唤醒、任务监控面板集成、键盘快捷键
✅ **动画**：基于状态的行为动画、平滑过渡、性能优化
✅ **扩展性**：宠物包插件系统、自定义动画支持、事件钩子系统
✅ **错误处理**：通信/渲染/输入错误的降级策略
✅ **测试**：单元/集成/E2E 三层覆盖
✅ **开发路径**：4 个阶段的清晰实现计划

该设计遵循 Moltbot 现有架构模式，与 Voice Wake 和 Gateway 深度集成，为用户提供直观、不打扰的任务状态可视化。
