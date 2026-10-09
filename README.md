# 图妈学法语 V0.5 — 一次性整包版

## 当前状态
- 50 道 TEF Canada 风格训练题：已重建并通过结构/编码审计
- 45 段独立音频脚本：已冻结
- 结果页：答对绿色 ✓；答错红色 ✕；明确显示“你的答案 / 正确答案”
- Android 包名：`com.tuma.french.app`
- V0.5 版本：`versionCode 3 / versionName 0.5`
- 手机端不依赖 Google Play / 系统 TTS
- 正式 APK 构建前会自动检查 50题、ABCD、乱码和45段音频

## 为什么现在没有把低质量音频塞进来
V0.4 已证明机械离线 TTS 不适合作为 TEF 训练音频。因此 V0.5 只接受高质量固定神经语音。

## 最省事的生产流程
上传这个整包到一个 **Private GitHub 仓库** 后，只需做一次：
1. 在 GitHub 仓库 Settings → Secrets and variables → Actions 中添加 Secret：`OPENAI_API_KEY`
2. Actions → `Generate V0.5 French Audio` → Run workflow
3. 工作流会一次生成 45 个固定 MP3，并自动提交回仓库
4. `Build Tuma French V0.5 APK` 随后自动检查并生成 APK
5. 下载 `tuma-french-v0.5-apk` 即可安装

API 只在生成这 45 段固定音频时调用一次；App 日常使用不调用 API。

## 音频标准
- France French，自然神经语音
- 正常 TEF 风格语速，只轻微慢于自然广播语流
- 对话/采访使用两种不同声音
- 公告、留言、街访、广播评论采用不同语体提示
- 音频与文字稿必须逐字一致

## 重要
此试用工程包含固定的试用签名材料，**仓库请保持 Private**。如果未来要公开发布或上架应用商店，需要换成正式私有签名密钥，不应把签名文件提交到公开仓库。
