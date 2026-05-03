---
title: "生物信息学 — 通往 bioSkills 和 ClawBio 提供的 400+ 生物信息学技能的网关"
sidebar_label: "生物信息学"
description: "通往 bioSkills 和 ClawBio 提供的 400+ 生物信息学技能的网关"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 生物信息学 {#bioinformatics}

通往 bioSkills 和 ClawBio 提供的 400+ 生物信息学技能的网关。涵盖基因组学、转录组学、单细胞、变异检测、药物基因组学、宏基因组学、结构生物学等。按需获取特定领域的参考资料。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/research/bioinformatics` 安装 |
| 路径 | `optional-skills/research/bioinformatics` |
| 版本 | `1.0.0` |
| 平台 | linux, macos |
| 标签 | `bioinformatics`, `genomics`, `sequencing`, `biology`, `research`, `science` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# 生物信息学技能网关 {#bioinformatics-skills-gateway}

当被问及生物信息学、基因组学、测序、变异检测、基因表达、单细胞分析、蛋白质结构、药物基因组学、宏基因组学、系统发育学或任何计算生物学任务时使用。

此技能是两个开源生物信息学技能库的网关。它不捆绑数百个领域特定技能，而是对它们进行索引，并按需获取所需内容。

## 来源 {#sources}

◆ **bioSkills** — 385 个参考技能（代码模式、参数指南、决策树）
  仓库：https://github.com/GPTomics/bioSkills
  格式：每个主题一个 SKILL.md，包含代码示例。Python/R/CLI。

◆ **ClawBio** — 33 个可运行管道技能（可执行脚本、可复现包）
  仓库：https://github.com/ClawBio/ClawBio
  格式：带演示的 Python 脚本。每个分析导出 report.md + commands.sh + environment.yml。

## 如何获取并使用技能 {#how-to-fetch-and-use-a-skill}

1. 从下方索引中确定领域和技能名称。
2. 克隆相关仓库（浅克隆以节省时间）：
   ```bash
   # bioSkills（参考资料）
   git clone --depth 1 https://github.com/GPTomics/bioSkills.git /tmp/bioSkills

   # ClawBio（可运行管道）
   git clone --depth 1 https://github.com/ClawBio/ClawBio.git /tmp/ClawBio
   ```
3. 读取特定技能：
   ```bash
   # bioSkills — 每个技能位于：<category>/<skill-name>/SKILL.md
   cat /tmp/bioSkills/variant-calling/gatk-variant-calling/SKILL.md

   # ClawBio — 每个技能位于：skills/<skill-name>/
   cat /tmp/ClawBio/skills/pharmgx-reporter/README.md
   ```
4. 将获取的技能作为参考资料使用。这些不是 Hermes 格式的技能——请将它们视为专家领域指南。它们包含正确的参数、合适的工具标志和经过验证的管道。

## 按领域划分的技能索引 {#skill-index-by-domain}

### 序列基础 {#sequence-fundamentals}
bioSkills：
  sequence-io/ — read-sequences, write-sequences, format-conversion, batch-processing, compressed-files, fastq-quality, filter-sequences, paired-end-fastq, sequence-statistics
  sequence-manipulation/ — seq-objects, reverse-complement, transcription-translation, motif-search, codon-usage, sequence-properties, sequence-slicing
ClawBio：
  seq-wrangler — 序列 QC、比对和 BAM 处理（封装 FastQC、BWA、SAMtools）
### 读段质量控制与比对 {#read-qc-alignment}
bioSkills:
  read-qc/ — 质量报告、fastp工作流、接头修剪、质量过滤、UMI处理、污染筛查、RNA-seq质量控制
  read-alignment/ — BWA比对、STAR比对、HISAT2比对、Bowtie2比对
  alignment-files/ — SAM/BAM基础、比对排序、比对过滤、BAM统计、重复处理、pileup生成

### 变异检测与注释 {#variant-calling-annotation}
bioSkills:
  variant-calling/ — GATK变异检测、DeepVariant、变异检测（bcftools）、联合检测、结构变异检测、过滤最佳实践、变异注释、变异标准化、VCF基础、VCF操作、VCF统计、一致性序列、临床解读
ClawBio:
  vcf-annotator — 基于祖先背景的VEP + ClinVar + gnomAD注释
  variant-annotation — 变异注释流程

### 差异表达（批量RNA-seq） {#differential-expression-bulk-rna-seq}
bioSkills:
  differential-expression/ — DESeq2基础、edgeR基础、批次校正、差异表达结果、差异表达可视化、时间序列差异表达
  rna-quantification/ — 免比对定量（Salmon/kallisto）、featureCounts计数、tximport工作流、计数矩阵质量控制
  expression-matrix/ — 计数数据导入、基因ID映射、元数据连接、稀疏数据处理
ClawBio:
  rnaseq-de — 包含质量控制、归一化和可视化的完整差异表达流程
  diff-visualizer — 差异表达结果的丰富可视化与报告

### 单细胞RNA-seq {#single-cell-rna-seq}
bioSkills:
  single-cell/ — 预处理、聚类、批次整合、细胞注释、细胞通讯、双细胞检测、标记物注释、轨迹推断、多模态整合、Perturb-seq、scATAC分析、谱系追踪、代谢通讯、数据输入输出
ClawBio:
  scrna-orchestrator — 完整的Scanpy流程（质量控制、聚类、标记物、注释）
  scrna-embedding — 基于scVI的潜在嵌入与批次整合

### 空间转录组学 {#spatial-transcriptomics}
bioSkills:
  spatial-transcriptomics/ — 空间数据输入输出、空间预处理、空间区域、空间解卷积、空间通讯、空间邻域、空间统计、空间可视化、空间多组学、空间蛋白质组学、图像分析

### 表观基因组学 {#epigenomics}
bioSkills:
  chip-seq/ — 峰检测、差异结合、基序分析、峰注释、ChIP-seq质量控制、ChIP-seq可视化、超级增强子
  atac-seq/ — ATAC峰检测、ATAC质量控制、差异可及性、足迹分析、基序偏差、核小体定位
  methylation-analysis/ — Bismark比对、甲基化检测、DMR检测、methylKit分析
  hi-c-analysis/ — Hi-C数据输入输出、TAD检测、环检测、区室分析、接触对、矩阵操作、Hi-C可视化、Hi-C差异分析
ClawBio:
  methylation-clock — 表观遗传年龄估计

### 药物基因组学与临床 {#pharmacogenomics-clinical}
bioSkills:
  clinical-databases/ — ClinVar查询、gnomAD频率、dbSNP查询、药物基因组学、多基因风险、HLA分型、变异优先级排序、体细胞特征、肿瘤突变负荷、myvariant查询
ClawBio:
  pharmgx-reporter — 基于23andMe/AncestryDNA的药物基因组学报告（12个基因、31个SNP、51种药物）
  drug-photo — 药物照片 → 个性化药物基因组学剂量卡（通过视觉）
  clinpgx — 用于基因-药物数据和CPIC指南的ClinPGX API
  gwas-lookup — 跨9个基因组数据库的联合变异查询
  gwas-prs — 基于消费级遗传数据的多基因风险评分
  nutrigx_advisor — 基于消费级遗传数据的个性化营养建议
### 群体遗传学与 GWAS {#population-genetics-gwas}
bioSkills:
  population-genetics/ — association-testing (PLINK GWAS), plink-basics, population-structure, linkage-disequilibrium, scikit-allel-analysis, selection-statistics
  causal-genomics/ — mendelian-randomization, fine-mapping, colocalization-analysis, mediation-analysis, pleiotropy-detection
  phasing-imputation/ — haplotype-phasing, genotype-imputation, imputation-qc, reference-panels
ClawBio:
  claw-ancestry-pca — 基于 SGDP 参考面板的祖先 PCA 分析

### 宏基因组学与微生物组 {#metagenomics-microbiome}
bioSkills:
  metagenomics/ — kraken-classification, metaphlan-profiling, abundance-estimation, functional-profiling, amr-detection, strain-tracking, metagenome-visualization
  microbiome/ — amplicon-processing, diversity-analysis, differential-abundance, taxonomy-assignment, functional-prediction, qiime2-workflow
ClawBio:
  claw-metagenomics — 鸟枪法宏基因组学分析（分类学、耐药组、功能通路）

### 基因组组装与注释 {#genome-assembly-annotation}
bioSkills:
  genome-assembly/ — hifi-assembly, long-read-assembly, short-read-assembly, metagenome-assembly, assembly-polishing, assembly-qc, scaffolding, contamination-detection
  genome-annotation/ — eukaryotic-gene-prediction, prokaryotic-annotation, functional-annotation, ncrna-annotation, repeat-annotation, annotation-transfer
  long-read-sequencing/ — basecalling, long-read-alignment, long-read-qc, clair3-variants, structural-variants, medaka-polishing, nanopore-methylation, isoseq-analysis

### 结构生物学与化学信息学 {#structural-biology-chemoinformatics}
bioSkills:
  structural-biology/ — alphafold-predictions, modern-structure-prediction, structure-io, structure-navigation, structure-modification, geometric-analysis
  chemoinformatics/ — molecular-io, molecular-descriptors, similarity-searching, substructure-search, virtual-screening, admet-prediction, reaction-enumeration
ClawBio:
  struct-predictor — 基于本地 AlphaFold/Boltz/Chai 的结构预测与比较

### 蛋白质组学 {#proteomics}
bioSkills:
  proteomics/ — data-import, peptide-identification, protein-inference, quantification, differential-abundance, dia-analysis, ptm-analysis, proteomics-qc, spectral-libraries
ClawBio:
  proteomics-de — 蛋白质组差异表达分析

### 通路分析与基因调控网络 {#pathway-analysis-gene-networks}
bioSkills:
  pathway-analysis/ — go-enrichment, gsea, kegg-pathways, reactome-pathways, wikipathways, enrichment-visualization
  gene-regulatory-networks/ — scenic-regulons, coexpression-networks, differential-networks, multiomics-grn, perturbation-simulation

### 免疫信息学 {#immunoinformatics}
bioSkills:
  immunoinformatics/ — mhc-binding-prediction, epitope-prediction, neoantigen-prediction, immunogenicity-scoring, tcr-epitope-binding
  tcr-bcr-analysis/ — mixcr-analysis, scirpy-analysis, immcantation-analysis, repertoire-visualization, vdjtools-analysis

### CRISPR 与基因组工程 {#crispr-genome-engineering}
bioSkills:
  crispr-screens/ — mageck-analysis, jacks-analysis, hit-calling, screen-qc, library-design, crispresso-editing, base-editing-analysis, batch-correction
  genome-engineering/ — grna-design, off-target-prediction, hdr-template-design, base-editing-design, prime-editing-design
### 工作流管理 {#workflow-management}
bioSkills:
  workflow-management/ — snakemake-workflows、nextflow-pipelines、cwl-workflows、wdl-workflows
ClawBio:
  repro-enforcer — 将任意分析导出为可复现性包（Conda 环境 + Singularity + 校验和）
  galaxy-bridge — 从 usegalaxy.org 访问 8,000 多个 Galaxy 工具

### 专业领域 {#specialized-domains}
bioSkills:
  alternative-splicing/ — 剪接定量、差异剪接、异构体切换、sashimi 图、单细胞剪接、剪接质控
  ecological-genomics/ — eDNA 宏条形码、景观基因组学、保护遗传学、生物多样性指标、群落生态学、物种界定
  epidemiological-genomics/ — 病原体分型、变异监测、系统动力学、传播推断、抗菌药物耐药监测
  liquid-biopsy/ — cfDNA 预处理、ctDNA 突变检测、片段分析、肿瘤分数估计、基于甲基化的检测、纵向监测
  epitranscriptomics/ — m6A 峰检出、m6A 差异分析、m6anet 分析、meRIP 预处理、修饰可视化
  metabolomics/ — XCMS 预处理、代谢物注释、归一化质控、统计分析、通路映射、脂质组学、靶向分析、MS-DIAL 预处理
  flow-cytometry/ — FCS 处理、门控分析、补偿变换、聚类分型、差异分析、细胞术质控、双联体检测、微球归一化
  systems-biology/ — 通量平衡分析、代谢重建、基因必需性、环境特异性模型、模型整理
  rna-structure/ — 二级结构预测、非编码 RNA 搜索、结构探测

### 数据可视化与报告 {#data-visualization-reporting}
bioSkills:
  data-visualization/ — ggplot2 基础、热图与聚类、火山图定制、Circos 图、基因组浏览器轨道、交互式可视化、多面板图、网络可视化、Upset 图、配色方案、专有组学图、基因组轨道
  reporting/ — R Markdown 报告、Quarto 报告、Jupyter 报告、自动化质控报告、图像导出
ClawBio:
  profile-report — 分析概况报告
  data-extractor — 从科学图表图像中提取数值数据（通过视觉识别）
  lit-synthesizer — PubMed/bioRxiv 搜索、摘要生成、引文图
  pubmed-summariser — 基于结构化的基因/疾病 PubMed 搜索简报

### 数据库访问 {#database-access}
bioSkills:
  database-access/ — Entrez 搜索、Entrez 获取、Entrez 链接、BLAST 搜索、本地 BLAST、SRA 数据、GEO 数据、UniProt 访问、批量下载、相互作用数据库、序列相似性
ClawBio:
  ukb-navigator — 跨 12,000 多个 UK Biobank 字段的语义搜索
  clinical-trial-finder — 临床试验发现

### 实验设计 {#experimental-design}
bioSkills:
  experimental-design/ — 效力分析、样本量、批处理设计、多重检验

### 组学机器学习 {#machine-learning-for-omics}
bioSkills:
  machine-learning/ — 组学分类器、生物标志物发现、生存分析、模型验证、预测解释、图谱映射
ClawBio:
  claw-semantic-sim — 疾病文献的语义相似度指数（基于 PubMedBERT）
  omics-target-evidence-mapper — 跨组学来源聚合靶点级别证据
## 环境设置 {#environment-setup}

这些技能假定你拥有一台生物信息学工作站。常见依赖项：

```bash
# Python
pip install biopython pysam cyvcf2 pybedtools pyBigWig scikit-allel anndata scanpy mygene

# R/Bioconductor
Rscript -e 'BiocManager::install(c("DESeq2","edgeR","Seurat","clusterProfiler","methylKit"))'

# CLI 工具（Ubuntu/Debian）
sudo apt install samtools bcftools ncbi-blast+ minimap2 bedtools

# CLI 工具（macOS）
brew install samtools bcftools blast minimap2 bedtools

# 或者通过 Conda（推荐，便于复现）
conda install -c bioconda samtools bcftools blast minimap2 bedtools fastp kraken2
```

## 常见陷阱 {#pitfalls}

- 获取到的技能**不是** Hermes SKILL.md 格式。它们使用自己的结构（bioSkills：代码模式 cookbook；ClawBio：README + Python 脚本）。请将其作为专家参考资料阅读。
- bioSkills 是参考指南——它们展示了正确的参数和代码模式，但并非可执行的流水线。
- ClawBio 技能是可执行的——许多带有 `--demo` 标志，可以直接运行。
- 两个仓库都假设生物信息学工具已安装。在运行流水线之前，请检查先决条件。
- 对于 ClawBio，先在克隆的仓库中运行 `pip install -r requirements.txt`。
- 基因组数据文件可能非常大。下载参考基因组、SRA 数据集或构建索引时，请注意磁盘空间。
