'use strict';
const catalogue = [
  {id:'dog-food',name:'Everyday canine nutrition',detail:'Adult dog food · 2 kg',price:3495,category:'dog',color:'sage',bag:'',icon:'🐕',label:'DAILY',type:'Canine nutrition'},
  {id:'cat-food',name:'Everyday feline nutrition',detail:'Adult cat food · 1.5 kg',price:2995,category:'cat',color:'peach',bag:'coral',icon:'🐈',label:'DAILY',type:'Feline nutrition'},
  {id:'dental',name:'Fresh-smile dental chews',detail:'For dogs · 14 chews',price:1850,category:'dog',color:'blue',bag:'blue-bag',icon:'◇',label:'SMILE',type:'Dental chews'},
  {id:'cat-treats',name:'Little rewards, big purrs',detail:'Cat treats · 80 g',price:895,category:'cat',color:'lilac',bag:'purple',icon:'♡',label:'LITTLE',type:'Happy rewards'}
];
const invoice = {id:'invoice',name:'Sample wellness invoice',detail:'DEMO-1042 · Alex & Charlie',price:9500};
const cart = new Map();
const money = cents => new Intl.NumberFormat('en-CA',{style:'currency',currency:'CAD'}).format(cents/100);
const $ = id => document.getElementById(id);
let toastTimer;
function notify(message){$('toast').textContent=message;$('toast').classList.add('visible');clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('toast').classList.remove('visible'),2200);}
function productById(id){return id==='invoice'?invoice:catalogue.find(product=>product.id===id);}
function renderProducts(filter='all'){
  $('products').innerHTML=catalogue.filter(p=>filter==='all'||p.category===filter).map(p=>`<article class="product"><div class="product-art ${p.color}"><span class="product-category">FOR ${p.category==='dog'?'DOGS':'CATS'} · SAMPLE</span><div class="bag ${p.bag}" aria-hidden="true"><b>${p.label}</b><span class="animal">${p.icon}</span><small>${p.type}</small></div></div><div class="product-info"><h4>${p.name}</h4><p>${p.detail}</p><div class="product-bottom"><strong>${money(p.price)}</strong><button class="add-button" data-add="${p.id}" aria-label="Add ${p.name} to cart">Add +</button></div></div></article>`).join('');
}
function total(){return [...cart].reduce((sum,[id,quantity])=>sum+productById(id).price*quantity,0);}
function renderCart(){
  $('cart-count').textContent=[...cart.values()].reduce((a,b)=>a+b,0);
  $('cart-total').textContent=money(total());
  $('checkout').disabled=cart.size===0;
  $('cart-items').innerHTML=cart.size?[...cart].map(([id,quantity])=>{const p=productById(id);return `<div class="cart-item"><div><strong>${p.name}</strong><small>${p.detail}</small>${id==='invoice'?'<button class="remove-invoice" data-remove="invoice">Remove invoice</button>':`<div class="quantity"><button data-change="${id}" data-delta="-1" aria-label="Decrease ${p.name} quantity">−</button><span aria-label="Quantity">${quantity}</span><button data-change="${id}" data-delta="1" aria-label="Increase ${p.name} quantity" ${quantity>=20?'disabled':''}>+</button></div>`}</div><strong>${money(p.price*quantity)}</strong></div>`;}).join(''):'<div class="empty-cart"><span>♡</span>A little empty, for now.<br>Add an essential or a sample invoice<br>to get started.</div>';
  $('add-invoice').disabled=cart.has('invoice');
  $('add-invoice').textContent=cart.has('invoice')?'Invoice added ✓':'Add invoice to summary +';
}
document.addEventListener('click',event=>{
  const add=event.target.closest('[data-add]');
  if(add){const id=add.dataset.add;const q=cart.get(id)||0;if(q>=20){notify('Demo limit: 20 per item.');return;}cart.set(id,q+1);renderCart();notify('Added to your demo summary');}
  const change=event.target.closest('[data-change]');
  if(change){const id=change.dataset.change;const q=(cart.get(id)||0)+Number(change.dataset.delta);if(q<=0)cart.delete(id);else cart.set(id,Math.min(q,20));renderCart();}
  if(event.target.closest('[data-remove]')){cart.delete('invoice');renderCart();}
  const filter=event.target.closest('[data-filter]');
  if(filter){document.querySelectorAll('[data-filter]').forEach(button=>{button.classList.toggle('active',button===filter);button.setAttribute('aria-pressed',String(button===filter));});renderProducts(filter.dataset.filter);}
});
const tabs=[$('shop-tab'),$('invoice-tab')];
function selectTab(tab){tabs.forEach(t=>{const active=t===tab;t.setAttribute('aria-selected',String(active));t.tabIndex=active?0:-1;$(t.getAttribute('aria-controls')).hidden=!active;});}
tabs.forEach((tab,index)=>{tab.addEventListener('click',()=>selectTab(tab));tab.addEventListener('keydown',event=>{let target;if(event.key==='ArrowRight'||event.key==='ArrowLeft')target=tabs[1-index];if(event.key==='Home')target=tabs[0];if(event.key==='End')target=tabs[1];if(target){event.preventDefault();selectTab(target);target.focus();}});});
$('invoice-form').addEventListener('submit',event=>{event.preventDefault();const valid=$('invoice-number').value.trim().toUpperCase()==='DEMO-1042'&&$('invoice-code').value.trim().toUpperCase()==='PET-2026';$('invoice-result').hidden=!valid;$('invoice-error').textContent=valid?'':'No sample invoice found. Use DEMO-1042 and client code PET-2026.';});
$('add-invoice').addEventListener('click',()=>{cart.set('invoice',1);renderCart();notify('Sample invoice added');});
const dialog=$('checkout-dialog');
document.querySelector('.close-dialog').addEventListener('click',()=>dialog.close());
dialog.addEventListener('click',event=>{if(event.target===dialog){const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)dialog.close();}});
$('checkout').addEventListener('click',()=>{
  if(!cart.size)return;
  $('checkout-content').innerHTML=`<p class="eyebrow">DEMO CHECKOUT</p><h2 id="checkout-title">One last look.</h2><p>Review your sample order. No payment details are needed and nothing will be sent to the hospital.</p><div class="review-lines">${[...cart].map(([id,q])=>`<div class="review-line"><span>${productById(id).name}${q>1?' × '+q:''}</span><strong>${money(productById(id).price*q)}</strong></div>`).join('')}<div class="review-line total"><span>Demo total</span><span>${money(total())}</span></div></div><p>Sample products: clinic pickup.<br>Sample invoice: simulated settlement only.</p><button id="confirm-demo" class="button">Simulate payment <span>→</span></button><p>No card charged. No order placed.</p>`;
  dialog.showModal();
  $('confirm-demo').addEventListener('click',()=>{const amount=money(total());const reference='DEMO-'+new Date().toISOString().replace(/\D/g,'').slice(0,14);$('checkout-content').innerHTML=`<div class="receipt-mark">✓</div><p class="eyebrow">SIMULATION COMPLETE</p><h2 id="checkout-title">All set. More time<br>for tail wags.</h2><p>Your demo checkout is complete.</p><div class="review-line"><span>Simulated total</span><strong>${amount}</strong></div><div class="review-line"><span>Demo reference</span><strong>${reference}</strong></div><p>This is a demonstration receipt. No money was collected, no invoice was paid, and no pickup order was created.</p><button id="finish-demo" class="button">Back to the client corner <span>↗</span></button>`;cart.clear();renderCart();$('finish-demo').addEventListener('click',()=>dialog.close());$('finish-demo').focus();},{once:true});
});
renderProducts();renderCart();
