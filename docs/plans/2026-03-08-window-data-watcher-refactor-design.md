# 窗口数据监控重构设计文档

## 背景

当前项目使用剪贴板监控方式获取数据，现需要重构为直接监控固定窗口的数据变化。

## 目标

将监控方式从剪贴板监控改为窗口数据监控，实时捕获TS1131.exe软件中"Item Properties"窗口的数据变化。

## 需求

1. 监控TS1131.exe进程的"Item Properties"窗口
2. 当窗口获得焦点时开始监控
3. 实时捕获TreeItemControl中"Set Value: {值}"格式的数据
4. 提取并显示值部分（如"wTZT_16064A"）
5. 支持软件多开，只监控焦点窗口

## 技术方案

### 方案选择：UI Automation事件监听

使用pywinauto库实现UI Automation事件监听，实时响应窗口数据变化。

**优点：**
- 实时响应数据变化，性能最优
- 精确定位到TreeItemControl
- 支持多窗口识别

### 目标控件定位策略

**定位特征：**
- 窗口标题：`Item Properties`
- 进程名：`TS1131.exe`
- 控件类型：`TreeItemControl`
- Name属性格式：`" Set Value: {值}"`
- 父控件类型：`QTreeWidget`

**定位逻辑：**
1. 检测TS1131.exe窗口获得焦点
2. 找到Item Properties窗口
3. 定位QTreeWidget控件
4. 遍历TreeItemControl，查找Name以"Set Value:"开头的项
5. 提取值部分

### 数据提取

使用正则表达式提取值：
```python
pattern = r"Set Value:\s*(.+)"
match = re.search(pattern, name)
value = match.group(1)  # 提取 "wTZT_16064A"
```

## 架构设计

### 组件变更

**需要移除的组件：**
- ClipboardWatcher的使用（保留类，移除main.py中的调用）

**需要新增的组件：**
- WindowDataWatcher：窗口数据监控器（基于UI Automation事件）
- target_window.json：目标窗口配置文件

**需要修改的组件：**
- UIAutomationReader：增强UI Automation事件监听能力
- FloatingWindow：移除对ClipboardWatcher的依赖
- main.py：调整初始化流程

### 数据流程

```
TS1131.exe窗口激活 
  → WindowFocusWatcher检测焦点
  → WindowDataWatcher启动监听QTreeWidget
  → TreeItemControl的Name属性变化
  → 提取值（去掉"Set Value:"前缀）
  → 发送到FloatingWindow显示
```

### 类设计

**WindowDataWatcher（新建）：**
```python
class WindowDataWatcher(QObject):
    data_changed = Signal(str)
    
    def __init__(self):
        # 初始化UI Automation
        # 加载目标窗口配置
        
    def start_watching(self, hwnd):
        # 监听指定窗口
        
    def stop_watching(self):
        # 停止监听
        
    def _on_data_change(self, name):
        # 处理数据变化
        # 提取值并发送信号
```

**配置文件结构（target_window.json）：**
```json
{
  "target_window": {
    "title": "Item Properties",
    "process_name": "TS1131.exe",
    "target_control": {
      "control_type": "TreeItemControl",
      "parent_class": "QTreeWidget",
      "name_pattern": "^\\s*Set Value:\\s*(.+)$"
    }
  }
}
```

## 文件结构

```
src/
  services/
    window_data_watcher.py  (新建)
    clipboard_watcher.py    (保留，不再使用)
    ui_automation_reader.py (增强)
  main.py                   (修改)
  ui/
    floating_window.py      (修改)
config/
  target_window.json        (新建)
```

## 错误处理

- 窗口不存在时：静默等待，不报错
- 控件不存在时：记录日志，继续监听
- pywinauto异常时：自动重连机制
- 窗口关闭时：自动停止监听

## 依赖

需要添加：
- `pywinauto`：用于UI Automation事件监听

## 实施步骤

1. 创建新分支进行重构
2. 添加pywinauto依赖
3. 创建target_window.json配置文件
4. 创建WindowDataWatcher服务
5. 增强UIAutomationReader功能
6. 修改FloatingWindow移除剪贴板依赖
7. 修改main.py调整初始化流程
8. 测试验证功能

## 风险与缓解

**风险1：pywinauto事件监听不稳定**
- 缓解：添加自动重连机制，超时重试

**风险2：控件定位失败**
- 缓解：使用多种定位策略，记录详细日志

**风险3：多窗口切换时的性能问题**
- 缓解：只在焦点窗口启动监听，非焦点窗口停止监听

## 测试计划

1. 单元测试：WindowDataWatcher的数据提取逻辑
2. 集成测试：窗口焦点切换时的监听启停
3. 端到端测试：TS1131.exe数据变化时的实时捕获
4. 多实例测试：软件多开时的焦点窗口切换

## 参考资料

- 目标窗口信息：目标窗口信息/111.json
- pywinauto文档：https://pywinauto.readthedocs.io/
- UI Automation文档：https://docs.microsoft.com/en-us/windows/win32/winauto/entry-uiauto-win32