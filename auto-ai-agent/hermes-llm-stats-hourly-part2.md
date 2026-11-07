---
type: LLM Prompt Fragment
title: Hermes llm stats hourly part 2
description: Hourly report seed queries and row interpretation; second of three ordered parts.
resource: prompt://dryvist/auto-ai-agent/hermes-llm-stats-hourly-part2
tags:
- hermes
- autonomous-agent
- cron
timestamp: '2026-11-07T07:35:00Z'
status: active
consumers:
- dryvist/ansible-proxmox-ai
render:
  engine: literal
  variables: []
  frontmatter: strip
source_history:
- repository: dryvist/ansible-proxmox-ai
  path: roles/hermes_agent/defaults/main/49-llm-stats-hourly.yml
  commit: e0a844dfb51e1447f0f118b5deb8fbc0c84b829b
  variable: hermes_agent_llm_stats_hourly_cron_prompt
---

SEED QUERIES. Q1 freshness per sourcetype: | tstats count AS events latest(_time) AS last_epoch WHERE index=llm earliest=-24h BY sourcetype | eval last_seen=strftime(last_epoch,"%F %T"), age_min=floor((now()-last_epoch)/60) | fields sourcetype events last_seen age_min | sort 0 - events Q2 hourly tokens and requests by model group: search index=llm sourcetype="litellm:proxy" earliest=-24h llm_request | dedup _raw | rex field=_raw "litellm\[\d+\]: (?<j>\{.*\})" | spath input=j | eval pt=tonumber(prompt_tokens), ct=tonumber(completion_tokens) | bin _time span=1h | stats sum(pt) AS prompt_tokens sum(ct) AS completion_tokens count AS requests BY _time model_group | sort 0 - _time model_group | eval hour=strftime(_time,"%m-%d %H:00") | fields hour model_group requests prompt_tokens completion_tokens Q3 same by serving host with success/failure: search index=llm sourcetype="litellm:proxy" earliest=-24h llm_request | dedup _raw | rex field=_raw "litellm\[\d+\]: (?<j>\{.*\})" | spath input=j | eval pt=tonumber(prompt_tokens), ct=tonumber(completion_tokens), serving_host=if(isnull(api_base) OR api_base IN ("","null"),"(none)",replace(replace(api_base,"^https?://",""),"[:/].*$","")), ok=if(status="success",1,0), bad=1-ok | bin _time span=1h | stats sum(ok) AS success sum(bad) AS failure count AS requests sum(pt) AS prompt_tokens sum(ct) AS completion_tokens BY _time serving_host | eval failure_pct=floor(1000*failure/requests)/10, hour=strftime(_time,"%m-%d %H:00") | sort 0 - _time serving_host | fields hour serving_host requests success failure failure_pct prompt_tokens completion_tokens Q4 errors by serving host and kind: search index=llm sourcetype="litellm:proxy" earliest=-24h llm_request | dedup _raw | rex field=_raw "litellm\[\d+\]: (?<j>\{.*\})" | spath input=j | eval serving_host=if(isnull(api_base) OR api_base IN ("","null"),"(none)",replace(replace(api_base,"^https?://",""),"[:/].*$","")) | where error_class!="" | eval kind=case(error_class IN ("RateLimitError","RouterRateLimitError"),"429", error_class IN ("Timeout","ReadTimeout"),"timeout", true(),"other") | stats count AS errors BY serving_host kind error_class | sort 0 - errors Q5 which host serves which model group now: search index=llm sourcetype="litellm:proxy" earliest=-1h llm_request | dedup _raw | rex field=_raw "litellm\[\d+\]: (?<j>\{.*\})" | spath input=j | where status="success" | eval serving_host=if(isnull(api_base) OR api_base IN ("","null"),"(none)",replace(replace(api_base,"^https?://",""),"[:/].*$","")) | stats count AS requests latest(_time) AS last_epoch BY model_group model serving_host | eval last_seen=strftime(last_epoch,"%T") | sort 0 - requests | fields model_group model serving_host requests last_seen Q6 Hermes API calls per host, profile and model group: search index=hermes earliest=-24h "API call #" | dedup _raw | rex field=_raw "^<\d+>\w+\s+\d+\s+[\d:]+\s+\S+\s+(?<profile>\S+)\s" | rex field=_raw "API call #(?<n>\d+): model=(?<model_group>\S+) provider=\S+ in=(?<tok_in>\d+) out=(?<tok_out>\d+)" | where isnotnull(n) | bin _time span=1h | stats count AS api_calls sum(tok_in) AS tokens_in sum(tok_out) AS tokens_out BY _time host profile model_group | eval hour=strftime(_time,"%m-%d %H:00") | sort 0 - _time host profile model_group | fields hour host profile model_group api_calls tokens_in tokens_out Per-request records are litellm:proxy lines with syslog-wrapped JSON, so fields are not auto-extracted and rex then spath is required. status=success in the base search returns zero rows, so filter after spath. On failures, api_base is the JSON string "null" and is shown as "(none)". dedup _raw removes doubled forwarded lines. Never use round(avg()) or countdistinct/dc inside a stats argument list; compute with eval afterwards. A tstats search must start with tstats.
Turn the rows into the report: show prompt and completion tokens per hour for the last 24 hours by model group and serving host, comparing this hour with the previous 24 hours and the recalled baseline; show failure percentage per serving host; count errors split into 429, timeout and other; identify which host serves each model group now; and show Hermes API calls per host, profile and model group. Keep the "Gaps:" line only for genuinely unavailable metrics, never for metrics these queries provide.
