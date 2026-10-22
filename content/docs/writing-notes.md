# 写作依据与验证范围

本文档供作者核对，不属于博客文章，不随文章复制进 content/posts。

## 源码范围

以下路径以 `/Users/windpro/Documents/Code/` 为根目录。

基础封装主要阅读 `tokenview_-v4/lib/` 下的 `model/ListEx.dart`、`model/MapEx.dart`、`component/custom_image.dart`、`utils/dialog_utils.dart`、`utils/sp_manager.dart`、`net/api_stream/` 及 `net/wallet_services.dart`。结合 tokenview、tokenview_-v2、tokenview_-v3 核对工具差异，没有根据目录名推断演进顺序。

IM 文章主要依据 `tokenview_-v2/lib/`：

- `pages/im/component/my_chat_list_view.dart`：日期行映射、构建时计数器、嵌套滚动结构。
- `pages/im/config/my_chat_controller.dart`：消息集合、广播流、历史插入、滚动监听、局部更新。
- `pages/im/chatroom/im_chatroom_controller.dart`：历史获取、接收消息、待展示消息、未读提示、引用定位。
- `pages/im/component/im_widgets/chat_bubble_widget.dart`、`message_view.dart`：气泡外壳、类型分发和 GlobalKey 的位置。
- `pages/im/component/im_widgets/message_type_view/image_message_view.dart`：网络、本地和内存图片的显示、占位和预览路径。
- `model/chat/chat_message.dart`：消息身份、发送状态、ValueNotifier 与组件 key。

滚动方向、布局时机和 ensureVisible 的解释另核对 Flutter 官方文档，相关链接在对应文章中。

## 本次实际验证

1. 从 Markdown 中提取集合分隔、严格整数/布尔解析、结果类型与日期行生成示例，用 Dart 3.11.1 执行断言；空列表、保持原集合、非法输入、跨日期分组等检查通过。
2. 从 Markdown 提取图片组件、确认框、偏好设置迁移、接近最新消息判断的完整声明，借用 v4 已解析依赖进行静态分析，结果为 No issues found。
3. 使用现有博客构建器临时发布全部文章，15 篇均生成 HTML。正式本地文章保留草稿标记。

列表 builder 等接入片段依赖文中说明的展示行与页面变量；历史分页和锚点保持使用流程描述，没有宣称是完整可运行实现。未运行四个完整应用，也没有测量设备滚动性能或修改项目源码。
