const input=document.querySelector('#search');
const buttons=[...document.querySelectorAll('[data-category]')];
let category='全部';
function filter(){const query=input.value.trim().toLocaleLowerCase();let visible=0;document.querySelectorAll('.post').forEach(post=>{const show=(category==='全部'||post.dataset.tag===category)&&post.textContent.toLocaleLowerCase().includes(query);post.hidden=!show;if(show)visible++;});document.querySelector('#empty').hidden=visible!==0;document.querySelector('#empty').textContent=document.querySelectorAll('.post').length?'没有找到相关文章，试试其他关键词或分类。':'暂无文章，第一篇内容正在准备中。';document.querySelector('#result-count').textContent=`${visible} 篇文章`;}
if(input){input.addEventListener('input',filter);buttons.forEach(button=>button.addEventListener('click',()=>{category=button.dataset.category;buttons.forEach(b=>b.setAttribute('aria-pressed',String(b===button)));filter();}));}
