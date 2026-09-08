/* Offline reader. Catalog facts stay unchanged; navigation is separately exportable. */
(() => {
  'use strict';
  const sourceDocument = '<!doctype html>\n' + document.documentElement.outerHTML;
  const data = JSON.parse(document.getElementById('catalog').textContent);
  const saved = JSON.parse(document.getElementById('initial-state').textContent);
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const textJSON = (v) => JSON.stringify(v).replace(/</g, '\\u003c').replace(/>/g, '\\u003e').replace(/&/g, '\\u0026');
  const icons = {
    folder:'<svg width="16" height="16" viewBox="0 0 20 20" aria-hidden="true"><path d="M2 5h6l2 2h8v10H2z" fill="none" stroke="currentColor" stroke-width="1.4"/></svg>',
    module:'<svg width="16" height="16" viewBox="0 0 20 20" aria-hidden="true"><path d="M3 3h5v5H3zM12 3h5v5h-5zM3 12h5v5H3zM12 12h5v5h-5z" fill="none" stroke="currentColor" stroke-width="1.3"/></svg>'
  };
  const state = {view:'files', snapshot:data.snapshots.at(-1)?.id, module:'', directory:'',
    query:'', nature:'', sort:'size', page:0, file:'', run:data.runs.at(-1)?.id || '',
    group:'nature', before:data.snapshots.at(-2)?.id || data.snapshots[0]?.id, ...saved};
  if (!['files','runs','storage'].includes(state.view)) state.view = 'files';
  if (!data.snapshots.some(s=>s.id === state.snapshot)) state.snapshot = data.snapshots.at(-1)?.id;
  const snap = () => data.snapshots.find(s=>s.id === state.snapshot);
  const findFile = (sid,path) => data.snapshots.find(s=>s.id===sid)?.files.find(f=>f.path===path);
  const moduleName = (id,s=snap()) => s?.map.modules.find(m=>m.id===id)?.title || '未归属模块';
  const baseName = (p) => p.split('/').at(-1);
  const dirName = (p) => p.includes('/') ? p.slice(0,p.lastIndexOf('/')) : '项目根目录';
  const formatBytes = (n) => {
    if (n === null || n === undefined) return '未知';
    if (!n) return '0 B';
    const u = Math.min(4,Math.floor(Math.log(n)/Math.log(1024)));
    return `${(n/1024**u).toLocaleString('en-US',{maximumFractionDigits:u?2:0})} ${['B','KiB','MiB','GiB','TiB'][u]}`;
  };
  const time = (s) => new Date(s).toISOString().replace('T',' ').slice(0,16) + ' UTC';
  const hashLabel = (f) => ({full:'完整 SHA-256',size_limit:'超出哈希上限',disabled:'未计算摘要',changed:'扫描时发生变化',unreadable:'内容不可读'}[f.hash_status] || '未知');
  const statusLabel = (s) => ({completed:'已完成 · 登记',failed:'失败 · 登记',cancelled:'已取消 · 登记'}[s] || '未知');
  const active = (yes) => yes ? ' aria-current="true"' : '';
  const button = (action,value,label,klass='',current=false) => `<button class="${klass}" data-action="${action}" data-value="${esc(value)}"${active(current)}>${label}</button>`;
  const fileButton = (f,sid,klass='file-button') => `<button class="${klass}" data-action="file" data-snapshot="${esc(sid)}" data-value="${esc(f.path)}">${esc(baseName(f.path))}<span class="directory">${esc(dirName(f.path))}</span></button>`;
  function toast(message) {
    $('notice').textContent=message; $('notice').classList.add('visible');
    clearTimeout(toast.timer); toast.timer=setTimeout(()=>$('notice').classList.remove('visible'),4000);
  }
  function snapshotOptions(selected) {
    return data.snapshots.map(s=>`<option value="${esc(s.id)}"${s.id===selected?' selected':''}>${esc(s.label)}</option>`).join('');
  }
  function filteredFiles() {
    const s=snap(); if (!s) return [];
    let files=s.files.filter(f=>(!state.module || (state.module==='__none' ? !f.module_id : f.module_id===state.module))
      && (!state.directory || f.path.startsWith(state.directory+'/'))
      && (!state.nature || (f.nature || '未分类')===state.nature)
      && (!state.query || `${f.path} ${f.nature || ''} ${moduleName(f.module_id)} ${f.format}`.toLowerCase().includes(state.query.toLowerCase())));
    return files.sort(state.sort==='path'?(a,b)=>a.path.localeCompare(b.path): (a,b)=>b.size_bytes-a.size_bytes || a.path.localeCompare(b.path));
  }
  function renderSidebar() {
    const s=snap(); if(!s){$('sidebar').innerHTML='<p>尚无快照</p>';return;}
    if(state.view==='runs') {
      $('sidebar').innerHTML='<h2>运行记录</h2><div class="side-list">'+data.runs.map(r=>button('run',r.id,`${esc(r.title)}<span class="count">${esc(r.status==='completed'?'完成':r.status==='failed'?'失败':'取消')}</span>`,'side-button',r.id===state.run)).join('')+'</div><div class="side-foot">每次运行有独立记录。失败或无新产物的尝试也可以保留。</div>';
      return;
    }
    const modules = s.map.modules;
    const directories = [...new Set(s.files.flatMap(f=>{
      const parts=f.path.split('/');return parts.slice(0,-1).map((_,i)=>parts.slice(0,i+1).join('/'));
    }))].sort();
    $('sidebar').innerHTML='<h2>模块</h2><div class="side-list">'+button('module','',`${icons.module}全部文件<span class="count">${s.files.length}</span>`,'side-button',!state.module)
      +modules.map(m=>button('module',m.id,`${icons.module}${esc(m.title)}<span class="count">${s.files.filter(f=>f.module_id===m.id).length}</span>`,'side-button',state.module===m.id)).join('')
      +(s.files.some(f=>!f.module_id)?button('module','__none','未归属模块','side-button',state.module==='__none'):'')
      +'</div><h2>目录</h2><div class="directory-list">'+button('directory','',`${icons.folder}项目根目录`,'side-button',!state.directory)
      +directories.slice(0,200).map(d=>button('directory',d,`${icons.folder}<span>${esc(d)}</span>`,'side-button',state.directory===d)).join('')
      +(directories.length>200?'<p class="small">显示前 200 个目录，可通过文件搜索查找完整路径。</p>':'')
      +'</div><div class="side-foot">'+(s.complete?'已完成指定范围扫描':'扫描不完整，部分内容未观察')+'<br>'+s.files.length+' 个文件 · '+s.skipped.length+' 项跳过<br>'+esc(time(s.captured_at))+'</div>';
  }
  function coverage() {
    const s=snap();
    return `<details class="coverage"><summary>扫描范围与口径 · ${s.skipped.length} 项跳过</summary><p class="section-note">隐藏项、依赖目录、常见凭证名称与符号链接默认跳过。扫描不保存文件正文，也不是原子文件系统快照。摘要上限 ${formatBytes(s.policy.hash_max_bytes)} / 文件。</p>`
      +(s.skipped.length?'<ul>'+s.skipped.slice(0,100).map(x=>`<li>${esc(x.path)} · ${esc(({excluded:'按规则排除',symlink:'符号链接',symlink_or_special:'链接或特殊文件',file_limit:'达到文件上限'})[x.reason] || x.reason)}</li>`).join('')+'</ul>':'')+'</details>';
  }
  function table(files, heading='文件') {
    const pages=Math.max(1,Math.ceil(files.length/200));state.page=Math.max(0,Math.min(state.page,pages-1));
    const rows=files.slice(state.page*200,(state.page+1)*200);
    if(!rows.length) return '<div class="empty"><h3>当前条件下没有文件</h3><p>调整模块、目录或搜索条件，查看其他文件。</p>'+button('reset','','清空筛选')+'</div>';
    return `<div class="table-wrap"><table aria-label="${esc(heading)}"><thead><tr><th>文件</th><th>业务性质</th><th>内容身份</th><th>逻辑大小</th></tr></thead><tbody>`
      +rows.map(f=>`<tr class="${state.file===f.path?'selected':''}"><td class="path-cell">${fileButton(f,state.snapshot)}</td><td>${esc(f.nature || '未分类')}</td><td><span class="tag ${f.content_id?'good':'warn'}">${f.content_id?'已计算':'未知'}</span></td><td class="num">${formatBytes(f.size_bytes)}</td></tr>`).join('')
      +`</tbody></table></div><div class="pagination"><span>${files.length} 个文件 · ${formatBytes(files.reduce((n,f)=>n+f.size_bytes,0))}</span><div><button data-action="page" data-value="-1"${state.page===0?' disabled':''}>上一页</button><span>${state.page+1} / ${pages}</span><button data-action="page" data-value="1"${state.page>=pages-1?' disabled':''}>下一页</button></div></div>`;
  }
  function filters() {
    return `<div class="toolbar"><label class="search">搜索文件<input id="search" type="search" value="${esc(state.query)}" placeholder="名称、路径或性质"></label><label>排序<select id="sort"><option value="size"${state.sort==='size'?' selected':''}>大小从高到低</option><option value="path"${state.sort==='path'?' selected':''}>文件路径</option></select></label>${button('reset','','清空筛选')}</div>`;
  }
  function renderFiles() {
    const s=snap();
    const chosen=s.map.modules.find(m=>m.id===state.module);
    $('main').innerHTML='<div class="section-head"><div><h2>'+esc(chosen?.title || '项目架构')+'</h2><p>'+esc(chosen?.purpose || '按职责找到文件，沿产物回看来源。')+'</p></div><span class="tag">职责由工作区映射声明</span></div>'
      +'<div class="module-map" aria-label="模块职责">'+s.map.modules.map(m=>button('module',m.id,`<strong>${esc(m.title)}</strong><p>${esc(m.purpose)}</p><div class="small num">${s.files.filter(f=>f.module_id===m.id).length} 个文件 · ${formatBytes(s.files.filter(f=>f.module_id===m.id).reduce((n,f)=>n+f.size_bytes,0))}</div>`,'module-node',state.module===m.id)).join('')+'</div>'
      +'<div class="relations" aria-label="声明的模块关系">'+s.map.relationships.map(r=>`<span>${button('module',r.source,esc(moduleName(r.source)))}<span class="relation-arrow">→ ${esc(r.label)} →</span>${button('module',r.target,esc(moduleName(r.target)))}</span>`).join('')+'</div>'
      +'<div class="breadcrumbs">'+button('reset','','全部文件')+(state.module?'<span>/</span>'+esc(moduleName(state.module)):'')+(state.directory?'<span>/</span>'+esc(state.directory):'')+(state.nature?'<span>/</span>'+esc(state.nature):'')+'</div>'
      +filters()+'<div id="file-results">'+table(filteredFiles())+'</div>'+coverage();
  }
  function refButtons(refs, role) {
    if(!refs.length) return `<p class="small">未登记${role}</p>`;
    return refs.map(ref=>{
      const f=findFile(ref.snapshot_id,ref.path);
      const s=data.snapshots.find(s=>s.id===ref.snapshot_id);
      return `<button data-action="ref" data-snapshot="${esc(ref.snapshot_id)}" data-value="${esc(ref.path)}"><strong>${esc(baseName(ref.path))}</strong><br><span class="small">${esc(s.label)} · ${formatBytes(f.size_bytes)} · ${f.content_id?'完整摘要':'摘要未知'}</span></button>`;
    }).join('');
  }
  function compareRows(before,after) {
    const a=new Map(before.files.map(f=>[f.path,f])), b=new Map(after.files.map(f=>[f.path,f]));
    const absent=(s,p)=>!s.complete || s.skipped.some(x=>p===x.path || p.startsWith(x.path+'/'));
    return [...new Set([...a.keys(),...b.keys()])].sort().map(path=>{
      const x=a.get(path), y=b.get(path);let change;
      if(!x) change=absent(before,path)?'此前未观察':'新增';
      else if(!y) change=absent(after,path)?'此后未观察':'移除';
      else if(!x.content_id || !y.content_id) change='内容未知';
      else change=x.content_id===y.content_id?'内容相同':'内容改变';
      return {path,before:x,after:y,change};
    });
  }
  function diffTable() {
    const before=data.snapshots.find(s=>s.id===state.before) || snap(), after=snap();
    const rows=compareRows(before,after), changed=rows.filter(r=>r.change!=='内容相同');
    return `<section class="run-compare"><h2>文件快照比较</h2><div class="diff-controls"><label>之前<select id="before">${snapshotOptions(before.id)}</select></label><label>之后<select id="after">${snapshotOptions(after.id)}</select></label></div>`
      +`<p class="section-note">${changed.length} 项变化或未知 · ${rows.length-changed.length} 项内容相同。同内容的新路径仍分别记为新增与移除。</p>`
      +(changed.length?'<div class="table-wrap"><table aria-label="文件快照差异"><thead><tr><th>文件</th><th>差异</th><th>之前</th><th>之后</th></tr></thead><tbody>'+changed.slice(0,200).map(r=>`<tr><td class="path-cell">${fileButton(r.after || r.before,r.after?after.id:before.id)}</td><td>${esc(r.change)}</td><td class="num">${r.before?formatBytes(r.before.size_bytes):'—'}</td><td class="num">${r.after?formatBytes(r.after.size_bytes):'—'}</td></tr>`).join('')+'</tbody></table></div>':'<p class="empty">这两个快照的已计算内容摘要相同。</p>')
      +(changed.length>200?'<p class="section-note">显示前 200 项。完整差异可使用 CLI diff 导出。</p>':'')+'</section>';
  }
  function renderRuns() {
    const run=data.runs.find(r=>r.id===state.run) || data.runs.at(-1);
    if(!run){$('main').innerHTML='<div class="empty"><h2>尚无运行记录</h2><p>用 record-run 导入输入、配置、产物和结论，再从这里回看实验来源。扫描时间无法推断实验经过。</p></div>'+diffTable();return;}
    state.run=run.id;
    const metricKeys=[...new Set(data.runs.flatMap(r=>Object.keys(r.metrics)))];
    $('main').innerHTML=`<div class="run-header"><h2>${esc(run.title)}</h2><div class="run-meta"><span class="tag ${run.status==='completed'?'good':'warn'}">${statusLabel(run.status)}</span><span>${esc(time(run.started_at))}</span><span class="mono">${esc(run.id)}</span></div></div>`
      +'<div class="lineage" aria-label="运行输入输出关系"><div class="lineage-files"><h3>输入</h3>'+refButtons(run.inputs,'输入')+'<h3>配置</h3>'+refButtons(run.config,'配置')+'</div><div class="lineage-arrow" aria-hidden="true">→</div><div class="lineage-files"><h3>产物</h3>'+refButtons(run.outputs,'产物')+'</div></div>'
      +'<p class="run-source">运行命令：<code>'+esc(run.command || '未登记')+'</code></p>'
      +'<section class="conclusion"><h3>结论 · 人工登记</h3><p>'+esc(run.conclusion || '未登记结论')+'</p><p class="small">记录依据：'+esc(run.evidence)+'</p></section>'
      +'<section class="run-compare"><h2>运行比较</h2><p class="section-note">指标来自运行记录。共同文件仅按完整摘要关联，指标比较不代表科学验证。</p><div class="table-wrap"><table aria-label="运行比较"><thead><tr><th>运行</th>'+metricKeys.map(k=>'<th>'+esc(k)+'</th>').join('')+'<th>产物</th></tr></thead><tbody>'
      +data.runs.map(r=>`<tr class="${r.id===run.id?'selected':''}"><td>${button('run',r.id,esc(r.title),'file-button')}</td>${metricKeys.map(k=>`<td class="num">${r.metrics[k]===undefined?'—':esc(r.metrics[k])}</td>`).join('')}<td>${r.outputs.length}</td></tr>`).join('')+'</tbody></table></div></section>'+diffTable();
  }
  function renderStorage() {
    const s=snap(), files=filteredFiles();const groups=new Map();
    const keyFor=(f)=>state.group==='nature'?(f.nature||'未分类'):state.group==='module'?moduleName(f.module_id):state.group==='format'?f.format:f.path.split('/').length>1?f.path.split('/')[0]:'项目根目录';
    for(const f of files){const key=keyFor(f);groups.set(key,(groups.get(key)||0)+f.size_bytes);}
    const total=files.reduce((n,f)=>n+f.size_bytes,0);
    $('main').innerHTML='<div class="section-head"><div><h2>存储分布</h2><p>查看大小，也看这些文件在项目里承担什么职责。</p></div></div>'
      +`<div class="stat-line"><div><strong>${formatBytes(s.summary.logical_bytes)}</strong><span>全快照逻辑大小 · ${s.files.length} 个路径</span></div><div><strong>${formatBytes(s.summary.allocated_bytes)}</strong><span>已分配字节 · 硬链接计一次</span></div></div>`
      +'<p class="storage-note">'+(s.synthetic_normalization?'合成样例的分配字节按 4 KiB 块归一化；逻辑大小与完整摘要经实际扫描。':'已分配字节来自文件系统报告。')+'分配字节不等于可回收空间，克隆、压缩与共享块可能影响实际释放量。下方按逻辑大小分组。</p>'
      +`<div class="toolbar"><label>分组方式<select id="group"><option value="nature"${state.group==='nature'?' selected':''}>业务性质</option><option value="module"${state.group==='module'?' selected':''}>模块</option><option value="format"${state.group==='format'?' selected':''}>文件格式（扩展名）</option><option value="directory"${state.group==='directory'?' selected':''}>顶层目录</option></select></label>${button('reset','','清空筛选')}</div>`
      +'<div class="distribution" aria-label="文件大小分布">'+[...groups].sort((a,b)=>b[1]-a[1]).map(([key,n])=>`<div class="bar-row"><span>${esc(key)}</span><div class="bar-track" role="img" aria-label="${esc(key)}占 ${total?(n/total*100).toFixed(1):0}%"><div class="bar-fill" style="width:${total?n/total*100:0}%"></div></div><span class="num">${formatBytes(n)}<br><small>${total?(n/total*100).toFixed(1):0}%</small></span></div>`).join('')+'</div><h2>文件明细</h2>'+filters()+'<div id="file-results">'+table(files,'存储文件明细')+'</div>'+coverage();
  }
  function renderInspector(animate=false) {
    const f=findFile(state.snapshot,state.file), s=snap();
    if(!f){$('inspector').innerHTML='<div class="empty"><h2>文件详情</h2><p>选择一个文件，查看所属模块、内容身份、生成运行和历史版本。</p></div>';return;}
    const exact=(ref)=>ref.snapshot_id===s.id && ref.path===f.path;
    const content=(ref)=>f.content_id && ref.content_id===f.content_id;
    const related=data.runs.filter(r=>[...r.inputs,...r.config,...r.outputs].some(ref=>exact(ref)||content(ref)));
    const history=data.snapshots.flatMap(s=>s.files.filter(x=>x.path===f.path).map(x=>({s,f:x})));
    const duplicates=s.files.filter(x=>x.path!==f.path && f.content_id && x.content_id===f.content_id);
    $('inspector').innerHTML=`<div class="${animate?'selection-enter':''}"><h2>${esc(baseName(f.path))}</h2><p class="file-path mono">${esc(f.path)}</p><dl><dt>所属模块</dt><dd>${esc(moduleName(f.module_id))}</dd><dt>业务性质</dt><dd>${esc(f.nature || '未分类')}<br><span class="small">工作区映射声明</span></dd><dt>文件格式</dt><dd>${esc(f.format)}<br><span class="small">按扩展名，未识别正文</span></dd><dt>逻辑大小</dt><dd class="num">${formatBytes(f.size_bytes)}<br><span class="small">${f.size_bytes.toLocaleString('en-US')} B</span></dd><dt>已分配字节</dt><dd class="num">${formatBytes(f.allocated_bytes)}${s.synthetic_normalization?'<br><span class="small">样例按 4 KiB 块归一化</span>':''}</dd><dt>所在快照</dt><dd>${esc(s.label)}</dd></dl>`
      +`<section><h3>内容身份</h3><span class="tag ${f.content_id?'good':'warn'}">${hashLabel(f)}</span>${f.content_id?'<div class="hash">'+esc(f.content_id)+'</div>':'<p class="section-note">当前观察没有完整内容摘要，不能据此判断版本相同。</p>'}${duplicates.length?'<p class="section-note">此快照还有 '+duplicates.length+' 个路径具有相同内容摘要。相同内容不代表可删除。</p>':''}</section>`
      +'<section><h3>相关运行</h3>'+ (related.length?related.map(r=>{
        const match=[...r.inputs,...r.config,...r.outputs].some(exact);
        const role=r.outputs.some(ref=>exact(ref)||content(ref))?'产物':r.config.some(ref=>exact(ref)||content(ref))?'配置':'输入';
        return button('run',r.id,`<strong>${esc(r.title)}</strong><span>${role} · ${match?'直接观察引用':'相同完整摘要关联'}</span>`,'history-row');
      }).join(''):'<p class="small">尚无引用此观察或相同内容的运行记录。文件时间不能证明生成过程。</p>')+'</section>'
      +'<section><h3>历次观察 · '+history.length+'</h3>'+reversed(history).map(({s:hs,f:hf})=>`<button class="history-row" data-action="ref" data-snapshot="${esc(hs.id)}" data-value="${esc(hf.path)}"${active(hs.id===s.id)}><strong>${esc(hs.label)}</strong><span>${formatBytes(hf.size_bytes)} · ${hf.content_id?esc(hf.content_id.slice(7,19)):'摘要未知'}</span></button>`).join('')+'</section></div>';
  }
  // Keep support for browsers that predate Array.prototype.toReversed.
  function reversed(items){return [...items].reverse();}
  function render() {
    $('project-title').textContent=data.project.title;
    $('project-meta').textContent=(data.project.synthetic?'合成研究项目':'本地项目')+' · '+data.snapshots.length+' 个快照 · '+data.runs.length+' 次运行 · 无账户，无联网';
    $('snapshot').innerHTML=snapshotOptions(state.snapshot);
    document.querySelectorAll('[data-view]').forEach(b=>{if(b.dataset.view===state.view)b.setAttribute('aria-current','page');else b.removeAttribute('aria-current');});
    renderSidebar();
    if(!snap()) {$('main').innerHTML='<div class="empty"><h2>尚无文件快照</h2><p>使用 scan 命令扫描指定目录，将元数据写入目录外的 catalog.json，然后重新生成工作台。</p></div>';renderInspector();return;}
    if(state.view==='runs')renderRuns();else if(state.view==='storage')renderStorage();else renderFiles();
    renderInspector();
  }
  function selectFile(sid,path) {
    if(!findFile(sid,path))return;
    state.snapshot=sid;state.file=path;
    locateSelectedFile();
    render();renderInspector(true);
    if(window.matchMedia('(max-width:1100px)').matches)$('inspector').scrollIntoView({behavior:'auto',block:'start'});
  }
  function locateSelectedFile() {
    if(!findFile(state.snapshot,state.file))return;
    if(!filteredFiles().some(f=>f.path===state.file)) {
      state.module='';state.directory='';state.query='';state.nature='';
    }
    state.page=Math.floor(filteredFiles().findIndex(f=>f.path===state.file)/200);
  }
  function focusDestination(element) {
    if(!element)return;
    if(!element.matches('button,input,select,a'))element.tabIndex=-1;
    element.focus({preventScroll:true});
    element.scrollIntoView({behavior:'auto',block:'start'});
  }
  document.addEventListener('click',event=>{
    const target=event.target.closest('button');if(!target)return;
    if(target.dataset.view){
      const fromRuns=state.view==='runs';
      state.view=target.dataset.view;state.page=0;
      if(state.view==='files')locateSelectedFile();
      render();
      if(fromRuns && state.view==='files')focusDestination($('main').querySelector('tr.selected button'));
      return;
    }
    const {action,value,snapshot}=target.dataset;
    if(!action)return;
    if(action==='file' || action==='ref'){selectFile(snapshot,value);return;}
    if(action==='module'){state.module=value;state.directory='';state.nature='';state.page=0;}
    if(action==='directory'){state.directory=value;state.page=0;}
    if(action==='reset'){state.module='';state.directory='';state.query='';state.nature='';state.page=0;}
    if(action==='run'){state.run=value;state.view='runs';}
    if(action==='page'){state.page+=Number(value);}
    render();
    if(action==='run')focusDestination($('main').querySelector('.run-header h2'));
  });
  document.addEventListener('input',event=>{
    if(event.target.id==='search'){
      state.query=event.target.value;state.page=0;
      if(state.view==='storage'){
        const start=event.target.selectionStart;renderStorage();const input=$('search');input.focus();input.setSelectionRange(start,start);
      }else $('file-results').innerHTML=table(filteredFiles());
    }
  });
  document.addEventListener('change',event=>{
    const {id,value}=event.target;
    if(id==='snapshot' || id==='after'){state.snapshot=value;state.page=0;}
    if(id==='before')state.before=value;
    if(id==='sort'){state.sort=value;state.page=0;}
    if(id==='group')state.group=value;
    if(['snapshot','after','before','sort','group'].includes(id))render();
  });
  function download(name,content,type){
    const blob=new Blob([content],{type});const url=URL.createObjectURL(blob);
    const a=document.createElement('a');a.href=url;a.download=name;document.body.appendChild(a);a.click();a.remove();
    setTimeout(()=>URL.revokeObjectURL(url),1000);
  }
  $('export-json').addEventListener('click',()=>{
    download('workspace-catalog.json',JSON.stringify(data,null,2),'application/json');toast('已导出目录与运行元数据。文件正文未包含在内。');
  });
  $('export-html').addEventListener('click',()=>{
    const opening='<script type="application/json" id="initial-state">';
    const start=sourceDocument.indexOf(opening), end=sourceDocument.indexOf('</script>',start);
    const output=sourceDocument.slice(0,start+opening.length)+textJSON(state)+sourceDocument.slice(end);
    download('architecture-workspace.html',output,'text/html');toast('已保存离线工作台，重新打开会回到当前阅读位置。');
  });
  render();
})();
