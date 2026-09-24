# 场景生成工作进展网页

内容快照：2026-09-24，截止 C01 封存。用途：日常更新、组会投屏、静态网页分享。本目录是独立 Git 仓库，远程为 `https://github.com/chilazy01-blip/chilazy01-blip.github.io.git`。不改写场景项目代码或实验产物。

## 打开与汇报

- 直接用浏览器打开 `public/index.html`。图片、视频、交互均使用相对路径，不需要联网或安装依赖。
- 换电脑时解压 `scene-report-offline.zip`，保留整个目录结构，再打开 `index.html`。不要只复制 HTML。
- 点击右上角“汇报模式”，一次显示一个部分；上下滚动查看本部分，左右方向键或底部按钮换部分，Esc 退出。浏览器 F11 可进一步全屏。
- 第三部分可筛选比较类别。第四部分可切换 RGB / 深度 / 实例标签，并播放或下载四段原始视频。
- 数值后的证据链接会展开原始记录摘要。原始报告、服务器路径、模型和训练数据未随公开网页上传。
- 打印按钮或浏览器打印可以另存 PDF；PDF 中视频只显示封面，正式展示建议使用网页。

## 内容与证据

- `content/report.json`：指标表、阶段、文献、对比、计划和证据摘要。
- `content/page.html`：静态页面模板，以及成果解读和文字说明。
- `public/style.css` / `public/app.js`：外观与渐进增强交互。
- `public/assets/`：原始展示图片/视频的逐字节副本。
- `content/assets.json`：公开素材的路径、大小与 SHA256，用于在独立仓库和 GitHub Actions 中校验素材。
- `source_manifest.json`：本地来源、SHA256、大小和采集时间，不用于公开部署。
- `public/evidence/snapshot.json`：公开的汇报内容摘要，不是实际训练数据包。
- `checks/static.py`：可在新克隆和 GitHub Actions 中运行的静态检查。
- `checks/` 下其他文件：本机浏览器脚本、截图、播放核验和打印预览；通过 `.gitignore` 留在本地。
- `.github/workflows/pages.yml`：推送到 `main` 后构建、检查并部署 `public/`。

历史 15 条轨迹只对应 2026-09-21 当时验收，不等于通过当前生产资格。O01 交付 1 份开发包；C01 关闭单例消费接口，不新增数据或训练结果。下一步是另外两个固定开发组合及保留组身份审计。网页不连接运行中的实验，不自动将未封存结果当作最新事实。

## 更新流程

1. 只读核对新封存报告，明确日期、验证范围、失败和未知项。
2. 同步修改 `content/report.json` 和 `content/page.html` 中的相关解读；单独更新一个数据文件不会自动改变所有正文。不要只改日期。
3. 在本目录运行 `python3 build.py`，重新生成 `public/index.html` 和 `public/evidence/snapshot.json`。这一步不读取或修改实验项目。
4. 如需刷新原始素材副本与本地来源哈希，再运行 `python3 build.py --copy-assets`。它仅从项目读取输入，写入本报告目录。
5. 运行 `python3 checks/static.py` 检查本地链接、锚点和公开文件路径；运行 `python3 build.py --verify-sources` 核验本轮引用输入是否发生变化。若原始项目同期更新，应核对新旧证据，不自动将变更视为损坏。
6. 用浏览器复查受影响的表格、图片和交互，再提交并推送本仓库的 `main` 分支，GitHub Actions 会发布 `public/` 的完整内容。离线包另行更新。

浏览器验收脚本为 `checks/browser.cjs`，当前环境复用了已安装的 Playwright 和 Chrome，路径写在脚本顶部；换机器时请改为自己的安装路径。网页本身不依赖这些工具。

## GitHub Pages 发布

目标账号：`chilazy01-blip`。仓库：`chilazy01-blip/chilazy01-blip.github.io`。

Git 仓库保存网页素材、页面模板、内容数据、构建脚本和发布配置；正式站点只部署 `public/`。不上传场景项目、实验文件、本地来源清单或浏览器检查记录。网站已经包含 `.nojekyll`，不需要 Node 或数据库。

首次启用：在仓库 **Settings → Pages → Build and deployment → Source** 中选择 **GitHub Actions**。然后在独立网页文件夹中提交并推送 `main`，或在 Actions 中手动运行 **Publish scene progress report**。设置 Pages 需要仓库管理或维护权限。

发布后预期网址为 `https://chilazy01-blip.github.io/`。是否已经上线，以 Actions 的成功部署和实际网页访问为准。

换电脑继续维护时，克隆本仓库即可：

```bash
git clone https://github.com/chilazy01-blip/chilazy01-blip.github.io.git
cd chilazy01-blip.github.io
python3 build.py
python3 checks/static.py
```

普通构建与素材检查不依赖场景项目或本机绝对路径。`--copy-assets` 和 `--verify-sources` 是原始工作区内的来源维护功能，换电脑后无需运行。

官方说明：https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages

账号切换、登录或授权应在 GitHub/连接设置界面完成，不要把密码或令牌写入本目录或对话。
