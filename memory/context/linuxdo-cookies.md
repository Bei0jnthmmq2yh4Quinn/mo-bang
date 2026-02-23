# Linux.do Cookies

用于绕过 Cloudflare 访问 linux.do，cookie 有过期时间需定期更新。

## 使用方式
```bash
curl -s \
  -H "Cookie: _t=<_t_value>; _forum_session=<session_value>; cf_clearance=<cf_value>" \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36" \
  "https://linux.do/t/topic/<id>.json"
```

## 当前 Cookie（2026-02-23 获取）
- **_t**: `lLCRQnQ1dWF0axy5GwJu3wC0b93QJ0yYvDd3jVK8U158bl2KRgBQYoVagHfGpIuQe5nU9ZJG5s4%2B7K%2FIM6g5jt6K9o%2FyI0Q%2BjCUeGvaP8tNTKXNKIXjzJgtYZ202DHCmlG8V%2Bf6KJS0djyDQSgozgeGnkBksUo4OMAHoVqJWu2Z%2B76JfjCDe1dHMCJGdXOuc2QxFHSLrWBELjavBjuj1kbBmoj%2Bwicmh6apvq%2FIfdTjIgkKDe9LGjx6YR%2BRwk9%2Bn%2F5G5%2FkuO%2Fcr4Iv0NLyGkAfNw4UfFipq%2BbcTHsSqikj8%3D--8AuEyXS3L%2B9DyewF--uqgykclloKQKS0aO%2FM7C4A%3D%3D`
  - 过期：2026-04-24
- **_forum_session**: `L2NuQaO%2BwPPk5IjeuEZM8ALZv0pr9R2k7jaXGry0VQoqwPZTGjogMUZ%2FQ0eBbtD9oWNDHU0T1drw4bRDLcrxu%2BydgYLzR6feqThNGIS2W7HJ0WHV%2FQpsgogRG32Qw%2FmM2mF8UjApRNupJo4mm5kXElwJ2L4DD151Bzlva4AdBvcbppn9h6evH3qc06RmE%2FW%2Bzb%2BQ2wPrw%2FXxRLPx0DkNGSPY8WBlkyQKUApk7KSKEbDFjsdNdPx4i6SNg7k%2B45EF4th4Wf5vWbEzh36cIJg%3D--3b3FTe3X%2BmhFfTUB--d0K0K4HrZZsxvFUHk2EOsw%3D%3D`
  - 过期：Session（浏览器关闭即失效，但 curl 可用）
- **cf_clearance**: `BRfUeBQ_LhVQi7q1M5f2pImpzkF34_79Jn7m8BzY2rU-1771854337-1.2.1.1-dK8e9A9QjugUmIr29G7D1fhe7dI.1QA8wEy0DXb2cMzz1WP4dLdn6tNB4FWgvyjJtqg3U8xWRmMYhcUOiNuWQ3df6ZEhWPz7gb5LCSho6J3s41fuu7uVD0g9iunCcoDDBO0vMCVSn205zUdveaKeDLQVMN98MYFQeISPTTPe5zOCyYHnNL69MQajDWxZkPOkJ2kzjr4O0hiFEXDR2ekmf3qaItDRGMMS._x_igz9DHph45NR9NMgr7Yl8otzGe1X`
  - 过期：2027-02-23

## 注意
- `cf_clearance` 绑定 User-Agent，必须用上面的 UA
- `_forum_session` 是 session cookie，可能较快失效
- `_t` 是持久登录 token，有效期到 4 月
- 失效后需要老板重新提供
