# 场景生成工作进展网页

计划更新：2026-10-09，新增第六页“问题与优化计划”，归纳 G1 全身主线的动作质量、场景适应与数据价值。前五部分保留 2026-09-28 的 MG/MD 历史快照，并有明确日期提示；文献核对沿用 2026-09-24。用途：日常更新、组会投屏、静态网页分享。本目录是独立 Git 仓库，远程为 `https://github.com/chilazy01-blip/chilazy01-blip.github.io.git`。不改写场景项目代码或实验产物。

## 打开与汇报

- 直接用浏览器打开 `public/index.html`。图片、视频、交互均使用相对路径，不需要联网或安装依赖。
- 换电脑时解压 `scene-report-offline.zip`，保留整个目录结构，再打开 `index.html`。不要只复制 HTML。
- 点击右上角“汇报模式”，一次显示一个部分；上下滚动查看本部分，左右方向键或底部按钮换部分，Esc 退出。浏览器 F11 可进一步全屏。
- 第三部分可筛选比较类别。第四部分先展示 Stretch 任务动图、批次数据与学习结果；历史区可展开查看 RGB / 深度 / 实例标签及四段原始视频。动图支持播放/停止，15 帧快放并非实际任务速度。
- 数值后的证据链接会展开原始记录摘要。原始报告、服务器路径、模型和训练数据未随公开网页上传。
- 打印按钮或浏览器打印可以另存 PDF；PDF 中视频只显示封面，正式展示建议使用网页。

新增计划页可直达 `https://chilazy01-blip.github.io/#plan-update`，也可在汇报模式中切到第六页。正文只呈现三类问题、优化方案和三步计划；详细验证范围收纳在页末。旧全身搬运视频未加入成果展示，也不用于证明稳定生产能力。

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

当前统一训练目录有 145 条成功开发轨迹，其中 92 条完整腕部 RGB-D；两数不能相加，验证/失败/评价和副本隔离。MG 56/56 批次通过；E 定位对照 3/24 对 22/24，但 W 完整视觉任务未通过；9 月 28 日 MD 六模型一步预测比较也未过门，固定分支已收束。下一步先形成可执行的控制/观测方案与独立任务准入，尚无已准入的自动任务后继。旧 Panda 15 条和 C01 包保留为历史，不并入当前统计。网页不连接运行中的实验，不自动将未封存结果当作最新事实。

## 更新流程

1. 只读核对新封存报告，明确日期、验证范围、失败和未知项。
2. 同步修改 `content/report.json` 和 `content/page.html` 中的相关解读；单独更新一个数据文件不会自动改变所有正文。不要只改日期。
3. 在本目录运行 `python3 build.py`，重新生成 `public/index.html` 和 `public/evidence/snapshot.json`。这一步不读取或修改实验项目。
4. 如需刷新原始素材副本与本地来源哈希，再运行 `python3 build.py --copy-assets`。它仅从项目读取输入，写入本报告目录。
5. 运行 `python3 checks/static.py` 检查本地链接、锚点和公开文件路径；运行 `python3 build.py --verify-sources` 核验本轮引用输入是否发生变化。若原始项目同期更新，应核对新旧证据，不自动将变更视为损坏。
6. 用浏览器复查受影响的表格、图片和交互，用户已于 2026-10-08 恢复发布请求。使用 GitHub Actions 时，提交并推送本仓库的 `main` 分支会发布 `public/`；应用连接的写权限与服务器 SSH 独立；服务器专用部署密钥已获授权，`publish.sh` 已完成首次推送和 GitHub Actions 部署。后续按下方持续发布方案执行。

浏览器验收脚本为 `checks/browser.cjs`，当前环境复用了已安装的 Playwright 和 Chrome，路径写在脚本顶部；换机器时请改为自己的安装路径。网页本身不依赖这些工具。

## GitHub Pages 发布

目标账号：`chilazy01-blip`。仓库：`chilazy01-blip/chilazy01-blip.github.io`。

Git 仓库保存网页素材、页面模板、内容数据、构建脚本和发布配置；正式站点只部署 `public/`。不上传场景项目、实验文件、本地来源清单或浏览器检查记录。网站已经包含 `.nojekyll`，不需要 Node 或数据库。

### 持续发布（推荐；2026-10-08 已上线）

独立目录中的 `publish.sh` 会构建、检查、提交并推送网页；GitHub Actions 随后自动部署 `public/`。页面包含 2026-10-09 的全身任务计划更新和 2026-09-28 的历史成果；执行发布不会自动更新实验进展或重新采集数据。

本服务器的以下两项设置已经完成，首次工作流成功部署，站点已显示汇报页面。后续更新直接执行 `./publish.sh`。以下步骤保留供更换服务器或重新配置时参考：

1. 登录 `chilazy01-blip`，打开 <https://github.com/chilazy01-blip/chilazy01-blip.github.io/settings/keys> → **Add deploy key**。Title 填 `scene-report-server`，Key 粘贴服务器 `checks/scene-report-deploy-key.pub` 的完整公钥，勾选 **Allow write access**，点击 **Add key**。此公钥对应的私钥仅保存在本仓库 `.git/scene-report-deploy/`，权限 600，不在提交或公开文件范围内。
2. 打开 <https://github.com/chilazy01-blip/chilazy01-blip.github.io/settings/pages>，在 **Build and deployment → Source** 中选择 **GitHub Actions**。仓库已有本地工作流，首次推送会上传，不必另选模板。

设置完成后，在服务器终端执行：

```bash
cd /data/wsj/main/scene_report_website
./publish.sh "Publish scene report"
```

以后每次修改本目录的汇报内容，仍使用同一命令，例如：

```bash
./publish.sh "Update report progress"
```

只做本地检查、不提交或推送：

```bash
./publish.sh --check
```

推送成功后到 <https://github.com/chilazy01-blip/chilazy01-blip.github.io/actions> 等待 `Publish scene progress report` 完成，再查看 <https://chilazy01-blip.github.io/>。本地保存文件不会自动推送；脚本也没有后台监听或定时运行。读取新实验记录、核实汇报内容仍在发布之前进行。

脚本仅暂存指定的网站路径；预先暂存了其他路径会拒绝。远端有未合并提交时会停止，保留双方内容，不强制推送。认证失败时先检查 Deploy key 是否完整、是否勾选写权限；无需更改 ChatGPT GitHub 应用连接。本服务器 SSH 设置仅对当前网页仓库有效，不改变全局 Git 或其他项目配置。换服务器后需另配密钥。

依据：[GitHub 部署密钥](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys)、[GitHub Pages 发布来源](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)。

### 浏览器上传（当前可自行完成）

这是首次自动部署前准备的手动备选方案。当前已使用服务器 SSH 推送与 GitHub Actions 上线，日常更新应使用上面的持续发布流程；若切换到手动上传，需要同时调整 Pages 来源和发布目录。GitHub 应用连接与服务器 SSH、VS Code 和浏览器登录相互独立。

1. 将 `checks/github-pages-upload-20261008.zip` 下载到自己的电脑并解压。包内是 40 个公开网站文件，内容快照仍为 2026-09-28。压缩包只包含 `public/` 的内容，没有外层 `public` 文件夹。
2. 在浏览器登录 `chilazy01-blip`，打开 <https://github.com/chilazy01-blip/chilazy01-blip.github.io/upload/main>（或仓库 Code → Add file → Upload files）。
3. 把解压目录**里面的文件和文件夹**拖入上传区，包括 `index.html`、`style.css`、`app.js`、`favicon.svg`、`assets/` 和 `evidence/`；隐藏的 `.nojekyll` 若未被选中，可在仓库 Add file → Create new file 中以该文件名创建，内容写 `Disable Jekyll`。不要上传 ZIP 本身，也不要多套一层文件夹。上传后 `index.html` 应与原 README 位于仓库同一层。选择直接提交到 `main`，点击 Commit changes。
4. 打开 <https://github.com/chilazy01-blip/chilazy01-blip.github.io/settings/pages>，将 Source 设为 **Deploy from a branch**，Branch 选 **main**，目录选 **/(root)**，点击 Save；已有相同设置则无需改动。本方案不选择 GitHub Actions 源。
5. 在仓库 Actions 页面查看 Pages 部署成功，再访问 <https://chilazy01-blip.github.io/>。若仍显示初始 README，先确认部署结束，再刷新浏览器缓存。

上传后的根目录应包含：

```text
README.md          原文件可保留
index.html
style.css
app.js
favicon.svg
.nojekyll
assets/            图片、视频、动图
evidence/          内含 snapshot.json
```

后续更新可重新生成并上传这套公开文件。若改用下面的 Git 推送/Actions 方案，应先获取并合并浏览器提交，核对根目录与 `public/` 的发布布局；不要强制推送覆盖远端。

### Git 推送与自动构建（具备终端写权限后）

在仓库 **Settings → Pages → Build and deployment → Source** 中选择 **GitHub Actions**。然后在独立网页文件夹中提交并推送 `main`，或在 Actions 中手动运行 **Publish scene progress report**。设置 Pages 需要仓库管理或维护权限。

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
