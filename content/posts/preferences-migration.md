---
title: SPManager 最该管的，其实是默认值和旧数据
date: 2024-03-12
category: 数据存储
author: Wesley
excerpt: 统一键名只是开始，初始化、异步写入与配置迁移决定了设置能否长期可用。
draft: false
---

一个设置刚加进来时，保存和读取都很简单。真正麻烦的是半年以后：枚举顺序变了，默认语言改了，旧安装留下的数据还在。

`SPManager` 把这些读写集中起来，让页面调用 `getAppLanguageMode()`，而不是到处认识某个存储键。这层封装值得继续保留，但职责不应该停在字符串常量。

### 枚举下标不是稳定协议

项目用枚举下标保存部分设置。问题在于下标代表声明顺序，后来在中间插入一项，旧数字就可能指向另一种含义。

更适合长期保存的是稳定代码，例如 `zh-CN`、`en-US`。迁移时，先尝试新键，再按旧版本明确的映射解释旧值。不能拿当前枚举顺序去猜旧数据。

下面是假设的语言设置迁移，使用已有 SharedPreferences API；旧映射仅为示例，接入时必须替换为真实历史约定：

```dart
Future<String> readLanguage(SharedPreferences prefs) async {
  const allowed = {'zh-CN', 'en-US'};
  final current = prefs.getString('language.v2');
  if (current != null && allowed.contains(current)) return current;

  const oldMapping = {0: 'en-US', 1: 'zh-CN'};
  final next = oldMapping[prefs.getInt('language.v1')] ?? 'en-US';
  final saved = await prefs.setString('language.v2', next);
  if (saved) await prefs.remove('language.v1');
  return next;
}
```

写新键成功后才移除旧键。写入失败时，这次读取仍可使用计算出的值，下次再尝试迁移。若旧键可能存了错误类型，还应增加读取失败的兼容处理，不能只依赖空值分支。

### 让调用方知道保存有没有完成

某些 setter 返回 `void`，底层写入结果被隐藏了。普通 UI 可以先乐观更新，但涉及退出页面前必须保存的设置，最好返回 Future，允许调用方等待、回退或提示失败。

初始化也要有明确顺序。项目先获取存储实例，再注入 `SPManager`；在此之前读取会碰到内部非空断言。初始化放在应用启动链路完成，不要让不同页面竞相初始化同一个管理器。

### 偏好设置不要承担所有本地数据

语言、显示选项适合偏好设置；可丢弃的接口响应适合缓存；敏感凭证需要单独的存储与访问策略。工具名字叫 SPManager，并不能证明里面的数据都适合 SharedPreferences。

把默认值、迁移和作用域留在这一层，页面代码反而能一直简单：它只需要知道当前设置，以及一次保存是否成功。
