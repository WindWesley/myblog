---
title: 接口字段一会儿是数字，一会儿是字符串，MapEx 应该兜到哪里
date: 2023-09-06
category: 工具封装
author: Wesley
excerpt: 解析层可以兼容数据形态，但不该替业务悄悄决定缺失值的含义。
draft: false
---

接口里同一个数量字段，有时返回 `12`，有时返回 `"12"`。每个页面都写一遍类型判断，时间久了，规则难免不一致。`MapEx.intFor` 把这段逻辑收起来，是很实用的做法。

更难的地方不是怎么转，而是转不了以后怎么办。

```dart
final count = data.intFor('count') ?? 0;
```

这行适合允许缺省的展示数量。如果读取的是必须存在的记录 ID，缺失值与零通常不是一回事。把两者合并，错误就会进入后面的请求，而不是停在解析边界。

### 兼容范围要窄，而且说得清楚

原实现接受整数和字符串，还会先移除小写 `0x`。复用时需要重新确认进制约定，不能去掉前缀后就假定已经完成十六进制解析。

如果接口只约定十进制整数，可以写得更保守：

```dart
int? readDecimalInt(Object? value) {
  if (value is int) return value;
  if (value is! String) return null;
  final text = value.trim();
  if (!RegExp(r'^[+-]?[0-9]+$').hasMatch(text)) return null;
  return int.tryParse(text);
}
```

`"12.5"`、`"0x10"`、`true` 都返回空值。调用方需要十六进制时，另写一个明确表达进制的入口，避免一个函数在不同接口间偷偷改变规则。

布尔值也一样。项目不同副本的 `boolFor` 对字符串支持不同，v4 会把任意非零整数当成真。这个规则在某些接口里合理，在只允许 0、1 的接口里就过于宽松。严格协议可以这样处理：

```dart
bool? readFlag(Object? value) {
  if (value is bool) return value;
  if (value is int && value == 0) return false;
  if (value is int && value == 1) return true;
  return null;
}
```

### 可空返回与异常是两回事

`doubleFor` 返回 `double?`，但字符串分支使用 `Decimal.parse`。非法内容仍可能抛异常。若这个入口用于普通展示数值，可以考虑 `double.tryParse`，并拒绝非有限值；如果需要精确小数计算，应继续保留 Decimal 类型，而不是解析后马上转成 double。

Map 扩展适合做小范围的数据兼容。到了“哪些字段必填”“缺失后是否拒绝整个对象”，就应交给模型解析。这样页面拿到的是可用对象，不是一堆需要继续猜测的字段。
