# 北京央国企 27 届校招追踪

> 面向 **27 届北交大硕士** 的每日自动校招聚合工具  
> Python 爬虫 + 本地静态网页，筛选北京央国企校招，过滤社招/外包/外地岗位

---

## 一、项目文件结构

```
beijing-soe-jobs/
├── README.md                 # 本说明文档
├── requirements.txt          # Python 依赖
├── config.yaml               # ★ 筛选规则配置（可手动修改）
├── main.py                   # 爬虫入口，运行此文件
│
├── crawler/                  # 爬虫核心代码
│   ├── models.py             # 岗位数据模型
│   ├── filter.py             # 筛选逻辑（读取 config.yaml）
│   ├── storage.py            # 去重、合并、保存 JSON
│   └── scrapers/             # 各数据源爬虫
│       ├── guopin.py         # 国聘网通用搜索（API）
│       ├── guopin_company.py # 按名录逐家检索国聘网
│       ├── mot_recruit.py    # ★ 交通运输部所属事业单位
│       ├── nra_recruit.py    # ★ 国家铁路局/铁道事业单位
│       ├── sasac.py          # 国资委人事专栏
│       └── company_sites.py  # 航天/航空/石油/中铁/中车/通号/北汽/京东方等官网
│
├── data/
│   ├── job.json              # 爬虫输出的原始数据
│   ├── catalog/                  # ★ 完整名录（230+ 家，6 类文件）
│   │   ├── 01_sasac_military.yaml    # 国资委-军工航天
│   │   ├── 02_sasac_energy.yaml      # 能源石油电网
│   │   ├── 03_sasac_industry.yaml    # 制造基建等
│   │   ├── 04_mof_finance.yaml       # 财政部-金融文化
│   │   ├── 05_beijing_municipal.yaml # 北京市属42家
│   │   └── 06_public_institutions.yaml # 事业编单位
│   ├── beijing_soe_directory.yaml  # 旧版名录（兼容）
│   └── institutions_extra.yaml     # 航天/交通/铁道补充
│
├── web/
│   ├── index.html            # ★ 招聘表格网页（浏览器打开）
│   ├── job.json              # 同步副本（供网页读取）
│   └── serve.py              # 本地预览服务器
│
├── scripts/
│   ├── run_crawler.sh        # 定时任务执行脚本
│   └── com.beijing.soe.jobs.plist  # macOS 每日定时配置模板
│
└── logs/                     # 运行日志
```

---

## 二、环境准备（一次性）

### 1. 确认已安装 Python 3.9+

```bash
python3 --version
```

### 2. 进入项目目录并创建虚拟环境

```bash
cd ~/Projects/beijing-soe-jobs
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 三、小白操作步骤

### 第一步：运行爬虫，抓取最新岗位

```bash
cd ~/Projects/beijing-soe-jobs
source .venv/bin/activate
python main.py
```

看到类似输出即表示成功：

```
国聘网: 原始 120 条 -> 筛选后 45 条
已保存 45 条岗位（本次新增 45 条）-> data/job.json
完成。共 45 条岗位，今日新增 45 条
```

数据会写入：
- `data/job.json`（备份）
- `web/job.json`（网页读取）

### 第二步：打开网页查看

**方式 A（推荐）—— 启动本地服务：**

```bash
python web/serve.py
```

浏览器打开：**http://localhost:8765**

**方式 B —— 直接双击 `web/index.html`：**

> 注意：浏览器安全策略下，直接打开 HTML 可能无法加载 JSON。  
> 若页面显示「加载失败」，请改用方式 A。

### 第三步：每日自动更新（可选）

见下方「定时任务配置」章节。

---

## 四、网页功能说明

| 功能 | 说明 |
|------|------|
| **专业筛选** | 工商管理/计算机/机械/电气等（匹配岗位专业要求） |
| **行业筛选** | 下拉选择航天/石油/汽车等行业 |
| **落户筛选** | 仅看带「落户」标签的岗位 |
| **收藏职位** | 点击 ☆ 收藏，筛选「仅收藏」；保存在浏览器本地 |
| 截止日期排序 | 按截止日升序/降序，7 天内标红 |
| 今日新增高亮 | 黄色背景行 + 「今日新增」标签 |
| 搜索 | 按公司名、岗位名、专业、来源模糊搜索 |
| 最后更新时间 | 页头显示爬虫上次运行时间 |

---

## 五、修改筛选规则

编辑 **`config.yaml`**，保存后重新运行 `python main.py` 即可。

### 常用修改示例

```yaml
filters:
  # 修改届别（如改为 26 届）
  graduate_years:
    - 26届
    - 2026届

  # 增加排除词
  exclude_keywords:
    - 社招
    - 外包
    - 你的自定义词

  # 增加关注的北京国企
  beijing_soe_companies:
    - 北汽
    - 京东方
    - 你的目标公司

  # 严格模式：必须同时满足届别+北京+国企
  strict_mode: true
```

### 开关数据源

```yaml
sources:
  guopin: true          # 国聘网通用搜索（推荐）
  guopin_company: true  # 按名录逐家检索（含 institutions_extra.yaml）
  mot_recruit: true     # ★ 交通运输部事业单位（交科院/公科院/规划院等）
  nra_recruit: true     # ★ 国家铁路局/铁道事业单位
  sasac: true           # 国资委
  company_sites: false  # 官网HTML抓取（反爬多，默认关）

guopin_company:
  use_all_keywords: false  # true=每家用全部别名搜索，更全但更慢（约10分钟）
```

### 增删企业名录

编辑 **`data/beijing_soe_directory.yaml`**，按格式添加企业：

```yaml
  - name: 你的目标公司
    category: 央企        # 或 北京市属
    industry: 金融
    search_keywords: ["公司简称", "全称关键词"]
```

保存后重新运行 `python main.py`。当前共 **269 家** 单位（去重后），涵盖：

| 类型 | 数量 | 说明 |
|------|------|------|
| 央企 | 130 | 国资委98家+下属研究院 |
| 事业单位 | 71 | 部委直属+北京市属+高校医院 |
| 北京市属 | 46 | 42家市属国企 |
| 金融央企 | 19 | 银行/保险/AMC |
| 文化央企 | 3 | 出版/电影等 |

增删单位可编辑 `data/catalog/` 下对应文件，或运行 `python scripts/build_catalog.py` 重新生成。

### 调整国聘搜索词

```yaml
guopin_keywords:
  - "2027"
  - "27届"
  - "管培"
  - "工商管理"   # 可加入你的专业关键词
```

---

## 六、定时任务配置（每日自动运行）

### macOS — launchd（推荐，一键安装）

```bash
cd ~/Projects/beijing-soe-jobs
bash scripts/install_launchd.sh
```

安装后每天 **8:00** 自动运行爬虫，日志在 `logs/launchd.out.log`。

手动测试：

```bash
bash scripts/run_crawler.sh
```

卸载：

```bash
launchctl unload ~/Library/LaunchAgents/com.beijing.soe.jobs.plist
```

**可选：爬完后自动推送到 GitHub**（让公网 Pages 也更新）：

编辑 `~/Library/LaunchAgents/com.beijing.soe.jobs.plist`，在 `ProgramArguments` 前加入：

```xml
<key>EnvironmentVariables</key>
<dict>
    <key>AUTO_PUSH</key>
    <string>1</string>
</dict>
```

然后 `launchctl unload` + `launchctl load` 重新加载。

### macOS — launchd（手动安装）

1. 编辑 `scripts/com.beijing.soe.jobs.plist`，将 `REPLACE_WITH_PROJECT_PATH` 替换为实际路径
2. 复制到 LaunchAgents 并加载（见旧版步骤，或直接用上方一键脚本）

### macOS / Linux — crontab

```bash
crontab -e
```

添加一行（每天 8:00 运行）：

```
0 8 * * * /bin/bash /Users/essence/Projects/beijing-soe-jobs/scripts/run_crawler.sh
```

### Windows — 任务计划程序

1. 打开「任务计划程序」→ 创建基本任务
2. 触发器：每天 8:00
3. 操作：启动程序
   - 程序：`python`
   - 参数：`main.py`
   - 起始于：`C:\path\to\beijing-soe-jobs`

---

## 七、GitHub 公网分享（一键部署）

把网页部署到 GitHub Pages 后，会得到固定公网链接，可直接发给同学查看。

**公网地址格式：** `https://你的GitHub用户名.github.io/beijing-soe-jobs/`

### 首次配置（约 5 分钟）

**方式 A — 自动脚本（已安装 `gh` 时推荐）**

```bash
cd ~/Projects/beijing-soe-jobs
chmod +x scripts/setup_github.sh
./scripts/setup_github.sh
```

脚本会：创建 GitHub 仓库 → 推送代码 → 提示后续两步。

**方式 B — 手动操作**

```bash
cd ~/Projects/beijing-soe-jobs
git add -A
git commit -m "Initial commit"
# 在 github.com 新建空仓库 beijing-soe-jobs 后：
git remote add origin git@github.com:你的用户名/beijing-soe-jobs.git
git push -u origin main
```

### 启用 GitHub Pages（仅需一次）

1. 打开仓库 **Settings → Pages**
2. **Build and deployment → Source** 选择 **GitHub Actions**
3. 打开 **Actions** 标签 → 左侧 **Deploy to GitHub Pages** → **Run workflow** → **Run workflow**
4. 等待约 5–15 分钟（首次含爬虫），绿色 ✓ 后访问上方公网链接

### 日常更新

| 方式 | 说明 |
|------|------|
| **本机自动** | 已安装 launchd 后，每天 8:00 本地爬取 |
| **GitHub 自动** | 每天北京时间 8:00 Actions 自动爬取并部署（新仓库 schedule 可能延迟 24h 首次触发） |
| **手动一键** | Actions → Deploy to GitHub Pages → Run workflow |
| **API 触发** | `export GITHUB_TOKEN=ghp_xxx && bash scripts/trigger_github_deploy.sh` |
| **本地更新后推送** | `python main.py` → `git add web/job.json` → `git commit` → `git push` |

> **schedule 未生效？** 仓库新建后 GitHub 定时任务可能延迟 1～2 天。可先用「手动一键」或 `scripts/trigger_github_deploy.sh` 触发；也可在 [cron-job.org](https://cron-job.org) 每天 8:05 调用 repository_dispatch API 作为备用。

### 国内访问（Gitee Pages 备用）

GitHub Pages（`*.github.io`）在国内经常打不开或极慢。一键配置 Gitee 镜像：

```bash
# 1. 在 https://gitee.com/profile/personal_access_tokens 申请令牌（勾选 projects）
# 2. 运行一键配置
export GITEE_USERNAME=你的Gitee用户名
export GITEE_TOKEN=你的令牌
export GITHUB_TOKEN=ghp_xxxx   # 可选，自动写入 GitHub Secrets
bash scripts/setup_gitee.sh
```

或分步：`python3 scripts/configure_gitee.py`

配置完成后，国内访问地址：

```
https://你的Gitee用户名.gitee.io/beijing-soe-jobs/
```

若首次打开 404，到 Gitee 仓库 → **服务 → Gitee Pages** → 分支选 `pages` → 启动。

GitHub Actions 在 GitHub Pages 部署成功后会自动同步到 Gitee（需配置 Secrets）。

### 分享给别人

直接把公网链接发给对方即可，例如：

```
https://zhangsan.github.io/beijing-soe-jobs/
```

对方无需安装 Python，手机/电脑浏览器均可打开。收藏功能仍保存在各自浏览器本地。

> 建议仓库设为 **Public**，GitHub Pages 和 Actions 免费额度更充足。

---

## 八、筛选逻辑说明

爬虫抓取后，按 `config.yaml` 中的规则过滤：

1. **排除** 标题/描述含「社招、外包、劳务派遣」等
2. **保留** 工作地点含「北京」
3. **保留** 公司名匹配央企关键词或北京国企白名单
4. **保留** 27 届 / 2027 届 / 校招 / 应届 相关岗位
5. **识别** 落户关键词，打上「落户」标签
6. **去重** 按「来源+公司+岗位+链接」生成唯一 ID，重复运行不会重复计数

---

## 九、常见问题

**Q: 国聘网能抓到，官网抓不到？**  
A: 部分央企官网有反爬或页面结构变化，可在 `config.yaml` 的 `company_sites` 中调整 `link_selector` 和 `title_must_contain`。国聘网是主数据源，通常已覆盖大部分央企岗位。

**Q: 岗位数量为 0？**  
A: 检查 `strict_mode` 是否过严；尝试设为 `false`。也可临时注释 `exclude_keywords` 排查。

**Q: 网页显示加载失败？**  
A: 必须先运行 `python main.py` 生成 `web/job.json`，再用 `python web/serve.py` 打开。不要直接双击 HTML 文件。

**Q: GitHub 公网链接打不开？**  
A: `*.github.io` 在国内不稳定。请用本机 `http://localhost:8765`，或配置 Gitee Pages 备用（见第七节「国内访问」）。

**Q: 为什么每天 8 点没有自动更新？**  
A: 检查三项：① 本机是否运行了 `bash scripts/install_launchd.sh`；② GitHub Actions schedule 对新仓库可能延迟；③ 仅 `push` 不会跑爬虫，需 schedule / 手动 Run workflow / API 触发。

**Q: 如何只看今日新增？**  
A: 网页排序选「今日新增优先」，黄色行即为今日新抓到的岗位。

---

## 十、命令速查

```bash
# 安装依赖
pip install -r requirements.txt

# 运行爬虫
python main.py

# 调试模式（更多日志）
python main.py -v

# 只抓取不保存
python main.py --dry-run

# 启动网页
python web/serve.py
```

---

**免责声明**：本项目仅供个人求职信息整理，数据来源于公开网站，请以各企业官方公告为准。
