---
# Leave the homepage title empty to use the site title
title: HZCU-HPCT
date: 2022-10-24
type: landing

sections:
  - block: hero
    content:
      title: |
        HZCU HPC Team
      image:
        filename: banner.jpg
      text: |
        <br>
        浙大城市学院高性能计算(HPC)团队是一个充满活力的学生团队，我们致力于高性能计算领域。
  
  - block: collection
    content:
      title:
      eyebrow: INTRODUCTION
      subtitle:
      text:
      count: 5
      filters:
        author: ''
        category: introduction
        exclude_featured: false
        publication_type: ''
        tag: ''
      offset: 0
      order: desc
      page_type: recruitment
    design:
      view: homepage-preview
      columns: '1'
    id: introduction

  - block: collection
    content:
      title:
      eyebrow: JOIN US
      subtitle:
      text:
      count: 5
      filters:
        author: ''
        category: join-us
        exclude_featured: false
        publication_type: ''
        tag: ''
      offset: 0
      order: desc
      page_type: recruitment
    design:
      view: homepage-preview
      columns: '1'
    id: join-us

# ERROR：Bao Zhuhan: 当前Publication页面无实际超链接，该部分停用
  # - block: collection
  #   content:
  #     title: Latest Preprints
  #     text: ""
  #     count: 5
  #     filters:
  #       folders:
  #         - publication
  #       publication_type: 'article'
  #   design:
  #     view: citation
  #     columns: '1'

  - block: markdown
    content:
      title:
      subtitle:
      text: |
        {{% cta cta_link="./people/" cta_text="Meet the team →" %}}
    design:
      columns: '1'


---
