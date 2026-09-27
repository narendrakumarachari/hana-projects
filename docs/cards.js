(function(){
var box=document.querySelector('.wires');
if(box){var key=box.getAttribute('data-key');var cbs=[].slice.call(box.querySelectorAll('input[type=checkbox]'));var pr=document.querySelector('.progress');
function load(){try{return JSON.parse(localStorage.getItem(key)||'[]')}catch(e){return[]}}
function save(){try{localStorage.setItem(key,JSON.stringify(cbs.filter(function(b){return b.checked}).map(function(b){return b.id})))}catch(e){}}
function upd(){var n=cbs.filter(function(b){return b.checked}).length;if(pr)pr.textContent=n===cbs.length?('All '+n+' done! Now upload the program.'):(n+' of '+cbs.length+' done')}
var s=load();cbs.forEach(function(b){b.checked=s.indexOf(b.id)!==-1;b.addEventListener('change',function(){save();upd()})});upd();}
[].slice.call(document.querySelectorAll('.copy')).forEach(function(btn){btn.addEventListener('click',function(){var el=btn.parentNode.querySelector('.path');var t=el.textContent;
function sel(){var r=document.createRange();r.selectNodeContents(el);var s=window.getSelection();s.removeAllRanges();s.addRange(r);btn.textContent='Selected: press Ctrl+C'}
if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(t).then(function(){btn.textContent='Copied!'},sel)}else{sel()}
setTimeout(function(){btn.textContent='Copy'},2500)})});
})();
