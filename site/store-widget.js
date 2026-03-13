(function(){
    var RECIPIENT='0x3570958b8dcbc4f663f508efcedb454ee9af9516';

    var CHAINS={
        '0x1':    {name:'Ethereum', usdc:'0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'},
        '0x2105': {name:'Base',     usdc:'0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913'},
        '0xa4b1': {name:'Arbitrum', usdc:'0xaf88d065e77c8cC2239327C5EDb3A432268e5831'},
        '0xa':    {name:'Optimism', usdc:'0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85'},
        '0x89':   {name:'Polygon',  usdc:'0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359'}
    };

    function esc(s){var d=document.createElement('div');d.textContent=s;return d.innerHTML;}
    function hexInt(h){return parseInt(h,16);}

    function formatSize(bytes){
        if(bytes<1024)return bytes+' B';
        if(bytes<1024*1024)return(bytes/1024).toFixed(1)+' KB';
        return(bytes/(1024*1024)).toFixed(1)+' MB';
    }

    function buildUsdcCalldata(priceAtomic){
        var recipHex=RECIPIENT.slice(2).toLowerCase().padStart(64,'0');
        var amountHex=priceAtomic.toString(16).padStart(64,'0');
        return '0xa9059cbb'+recipHex+amountHex;
    }

    function waitForReceipt(txHash){
        var attempts=0;
        return new Promise(function(resolve,reject){
            (function poll(){
                ethereum.request({method:'eth_getTransactionReceipt',params:[txHash]}).then(function(receipt){
                    if(receipt)return resolve({receipt:receipt,txHash:txHash});
                    if(++attempts>90)return reject(new Error('Transaction timeout.'));
                    setTimeout(poll,2000);
                }).catch(reject);
            })();
        });
    }

    function getStoredToken(productId){
        try{
            var data=JSON.parse(localStorage.getItem('dltoken:'+productId));
            if(data && data.expiresAt>Date.now())return data.token;
            localStorage.removeItem('dltoken:'+productId);
        }catch(e){}
        return null;
    }

    function storeToken(productId,token,expiresAt){
        try{
            localStorage.setItem('dltoken:'+productId,JSON.stringify({token:token,expiresAt:expiresAt}));
        }catch(e){}
    }

    function connectWallet(cb){
        if(!window.ethereum)return;
        ethereum.request({method:'eth_requestAccounts'}).then(function(accounts){
            if(!accounts.length)return;
            return ethereum.request({method:'eth_chainId'}).then(function(c){
                if(cb)cb(accounts[0],c);
            });
        }).catch(function(){});
    }

    function initEmbed(el){
        var productId=el.getAttribute('data-product');
        if(!productId)return;

        el.innerHTML='<p style="color:var(--meta-color);font-size:0.9em;">Loading...</p>';

        fetch('/api/products?id='+encodeURIComponent(productId))
            .then(function(r){return r.json();})
            .then(function(d){
                if(!d.product){el.innerHTML='';return;}
                var p=d.product;
                var existingToken=getStoredToken(p.id);

                var html='<div style="border:1px solid var(--border-color);border-radius:8px;overflow:hidden;margin:1.5em 0;">';
                if(p.imageUrl){
                    html+='<div style="aspect-ratio:16/9;overflow:hidden;background:rgba(0,0,0,0.03);">';
                    html+='<img src="'+esc(p.imageUrl)+'" alt="'+esc(p.title)+'" style="width:100%;height:100%;object-fit:cover;display:block;" loading="lazy">';
                    html+='</div>';
                }
                html+='<div style="padding:1.2em;">';
                html+='<h3 style="margin:0 0 0.3em;font-size:1.1em;">'+esc(p.title)+'</h3>';
                if(p.description)html+='<p style="color:var(--meta-color);font-size:0.9em;margin:0 0 0.8em;line-height:1.5;">'+esc(p.description)+'</p>';
                html+='<div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:0.5em;">';
                html+='<div><span style="font-weight:600;">'+esc(p.priceDisplay)+'</span> <span style="font-size:0.8em;color:var(--meta-color);">'+formatSize(p.totalFileSize)+'</span>';
                if(p.files.length>1)html+=' <span style="font-size:0.8em;color:var(--meta-color);">'+p.files.length+' files</span>';
                html+='</div>';
                html+='<span>';
                html+='<button class="store-widget-buy" style="background:var(--text-color);color:var(--bg-color);border:1px solid var(--text-color);padding:0.5em 1.5em;border-radius:4px;cursor:pointer;font-family:var(--font-body);font-size:0.9em;">Buy</button>';
                if(existingToken){
                    if(p.files.length>1){
                        html+=' <span class="store-widget-redownload" style="font-size:0.85em;color:var(--link-color);cursor:pointer;text-decoration:underline;">files</span>';
                    }else{
                        html+=' <span class="store-widget-redownload" style="font-size:0.85em;color:var(--link-color);cursor:pointer;text-decoration:underline;">re-download</span>';
                    }
                }
                html+='</span>';
                html+='</div>';
                html+='<p class="store-widget-status" style="margin-top:0.5em;font-size:0.85em;color:var(--meta-color);"></p>';
                html+='</div>';
                html+='</div>';
                el.innerHTML=html;

                var statusEl=el.querySelector('.store-widget-status');
                var buyBtn=el.querySelector('.store-widget-buy');
                var redownloadEl=el.querySelector('.store-widget-redownload');

                function setStatus(msg){statusEl.textContent=msg;}
                function setStatusHtml(h){statusEl.innerHTML=h;}

                function showDownloadLinks(token){
                    var h='<strong>Download your files:</strong><br>';
                    for(var i=0;i<p.files.length;i++){
                        h+='<a href="/api/download?token='+encodeURIComponent(token)+'&file='+i+'" style="display:inline-block;margin:0.3em 0;">'+esc(p.files[i].filename)+' ('+formatSize(p.files[i].fileSize)+')</a><br>';
                    }
                    setStatusHtml(h);
                }

                if(redownloadEl){
                    redownloadEl.onclick=function(){
                        var token=getStoredToken(p.id);
                        if(!token){setStatus('Token expired. Please purchase again.');return;}
                        if(p.files.length>1){
                            showDownloadLinks(token);
                        }else{
                            window.location.href='/api/download?token='+encodeURIComponent(token)+'&file=0';
                        }
                    };
                }

                function executeBuy(walletAddr,walletChain){
                    var chain=CHAINS[walletChain];
                    if(!chain){setStatus('Please switch to a supported network.');return;}

                    var txPromise;
                    if(p.currency==='eth'){
                        var weiHex='0x'+BigInt(p.price).toString(16);
                        setStatus('Sending '+p.priceDisplay+' on '+chain.name+'\u2026');
                        txPromise=ethereum.request({
                            method:'eth_sendTransaction',
                            params:[{from:walletAddr,to:RECIPIENT,value:weiHex}]
                        });
                    }else{
                        var calldata=buildUsdcCalldata(p.price);
                        setStatus('Sending '+p.priceDisplay+' on '+chain.name+'\u2026');
                        txPromise=ethereum.request({
                            method:'eth_sendTransaction',
                            params:[{from:walletAddr,to:chain.usdc,data:calldata}]
                        });
                    }

                    txPromise.then(function(txHash){
                        setStatus('Confirming on '+chain.name+'\u2026');
                        return waitForReceipt(txHash);
                    }).then(function(result){
                        if(result.receipt.status!=='0x1'){
                            setStatus('Transaction failed on chain.');
                            return;
                        }
                        setStatus('Verifying payment\u2026');
                        return fetch('/api/purchase',{
                            method:'POST',
                            headers:{'Content-Type':'application/json'},
                            body:JSON.stringify({productId:p.id,txHash:result.txHash,address:walletAddr,chainId:hexInt(walletChain)})
                        }).then(function(r){return r.json();});
                    }).then(function(data){
                        if(!data)return;
                        if(data.success){
                            storeToken(p.id,data.downloadToken,Date.now()+24*60*60*1000);
                            if(p.files.length>1){
                                showDownloadLinks(data.downloadToken);
                            }else{
                                setStatus('Starting download\u2026');
                                window.location.href='/api/download?token='+encodeURIComponent(data.downloadToken)+'&file=0';
                            }
                        }else{
                            setStatus(data.error||'Purchase failed.');
                        }
                    }).catch(function(err){
                        if(err.code===4001){setStatus('Transaction cancelled.');return;}
                        setStatus(err.message||'Something went wrong.');
                    });
                }

                buyBtn.onclick=function(){
                    if(!window.ethereum){
                        setStatus('Open in MetaMask or Coinbase Wallet to purchase.');
                        return;
                    }
                    // Connect then buy in one flow
                    setStatus('Connecting wallet\u2026');
                    connectWallet(function(walletAddr,walletChain){
                        executeBuy(walletAddr,walletChain);
                    });
                };
            })
            .catch(function(){
                el.innerHTML='';
            });
    }

    // Initialize all embed elements on the page
    var embeds=document.querySelectorAll('.store-embed');
    for(var i=0;i<embeds.length;i++){
        initEmbed(embeds[i]);
    }
})();
