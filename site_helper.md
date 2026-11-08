(function() {
  const table = document.querySelector('table.rating_table');
  if (!table) return alert('Tabela de warehouse não encontrada!');

  const rows = Array.from(table.querySelectorAll('tbody > tr')).filter(
    tr => tr.querySelector('.itembase_icon_Icon, .itembase_icon_Icon2')
  );

  const grid = document.createElement('div');
  grid.style.display = 'grid';
  grid.style.gridTemplateColumns = 'repeat(10, 1fr)';
  grid.style.gap = '8px';
  grid.style.padding = '10px 0';

  // Custom style for selection, hover, and tooltip BELOW the icon
  const style = document.createElement('style');
  style.textContent = `
    .craft_item_element {
      transition: box-shadow 0.13s, background 0.13s;
      position: relative;
    }
    .craft_item_element.selected {
      box-shadow: 0 0 0 2px #1e9cff, 0 2px 8px #0002 !important;
      background: rgba(30,156,255,0.09) !important;
    }
    .craft_item_element:not(.selected):hover {
      box-shadow: 0 0 0 2px #77f07fbb, 0 2px 8px #0001;
      background: rgba(119,240,127,0.10);
    }
    .craft_item_element .warehouse_item_info {
      pointer-events: none !important;
      position: absolute !important;
      top: 48px !important; /* Exibe tooltip abaixo do ícone, ajuste conforme o tamanho do seu ícone */
      left: 50%;
      transform: translateX(-50%);
      z-index: 30;
      min-width: 200px;
      max-width: 340px;
      background: rgba(18, 21, 31, 0.98);
      padding: 10px 18px 10px 10px;
      border-radius: 9px;
      box-shadow: 0 6px 32px #0009;
      font-size: 14px;
      color: #fff;
      opacity: 0;
      transition: opacity .18s;
      visibility: hidden;
    }
    .craft_item_element._hovering .warehouse_item_info {
      opacity: 1;
      visibility: visible;
      pointer-events: auto;
    }
  `;
  document.head.appendChild(style);

  rows.forEach((tr, idx) => {
    const icon = tr.querySelector('.itembase_icon_Icon, .itembase_icon_Icon2');
    if (!icon) return;
    const info = icon.nextElementSibling && icon.nextElementSibling.classList.contains('warehouse_item_info')
      ? icon.nextElementSibling
      : null;

    let qtd = '';
    const counts = tr.querySelectorAll('.warehouse_td_count');
    if (counts.length > 0) {
      for (let el of counts) {
        const txt = el.textContent.trim();
        if (/^\d+$/.test(txt)) { qtd = txt; break; }
      }
    }

    let server_id = '';
    if (info) {
      const serverDiv = Array.from(info.querySelectorAll('div')).find(div => div.textContent.includes('serverid:'));
      if (serverDiv) {
        const parts = serverDiv.textContent.split('serverid:');
        if (parts[1]) server_id = parts[1].trim();
      }
    }

    const label = document.createElement('label');
    label.className = 'craft_item_element';
    label.style.cursor = 'pointer';
    label.style.display = 'flex';
    label.style.flexDirection = 'column';
    label.style.alignItems = 'center';
    label.style.userSelect = 'none';

    // No more checkbox
    label.dataset.serverId = server_id;

    const logoDiv = document.createElement('div');
    logoDiv.className = 'craft_item_logo';
    logoDiv.style.position = 'relative';
    logoDiv.style.display = 'flex';
    logoDiv.style.justifyContent = 'center';
    logoDiv.style.alignItems = 'center';

    // Hover/Tooltip control (não pisca mais!)
    let hoverTimeout;
    logoDiv.addEventListener('mouseenter', () => {
      clearTimeout(hoverTimeout);
      label.classList.add('_hovering');
    });
    logoDiv.addEventListener('mouseleave', () => {
      hoverTimeout = setTimeout(() => {
        label.classList.remove('_hovering');
      }, 40);
    });

    logoDiv.appendChild(icon.cloneNode(true));

    if (qtd) {
      const badge = document.createElement('div');
      badge.textContent = qtd;
      badge.style.position = 'absolute';
      badge.style.bottom = '2px';
      badge.style.right = '6px';
      badge.style.background = 'rgba(0,0,0,0.7)';
      badge.style.color = '#fff';
      badge.style.borderRadius = '8px';
      badge.style.padding = '1px 6px';
      badge.style.fontSize = '12px';
      badge.style.fontWeight = 'bold';
      badge.style.pointerEvents = 'none';
      badge.style.zIndex = 2;
      logoDiv.appendChild(badge);
    }

    if (info) label.appendChild(info.cloneNode(true));
    label.appendChild(logoDiv);

    // Click to select/unselect
    label.addEventListener('click', function(e) {
      if (e.target.closest('.warehouse_item_info')) return;
      label.classList.toggle('selected');
    });

    grid.appendChild(label);
  });

  table.parentNode.insertBefore(grid, table);
  table.remove();

  // ===== LOADING ELEMENT =====
  const loading = document.createElement('div');
  loading.style.position = 'fixed';
  loading.style.top = 0;
  loading.style.left = 0;
  loading.style.width = '100vw';
  loading.style.height = '100vh';
  loading.style.background = 'rgba(20,24,36,0.75)';
  loading.style.display = 'flex';
  loading.style.alignItems = 'center';
  loading.style.justifyContent = 'center';
  loading.style.zIndex = 9999;
  loading.style.flexDirection = 'column';
  loading.style.fontFamily = 'Arial, sans-serif';
  loading.style.fontSize = '2rem';
  loading.style.color = '#fff';
  loading.innerHTML = `
    <div style="display:flex;flex-direction:column;align-items:center;">
      <div class="spinner" style="margin-bottom:22px;width:64px;height:64px;border:8px solid #77f07f;border-top:8px solid #1e9cff;border-radius:50%;animation:spin1 1s linear infinite"></div>
      <div>Enviando itens...</div>
    </div>
    <style>
      @keyframes spin1 { 100% { transform: rotate(360deg);} }
    </style>
  `;
  loading.style.display = "none";

  document.body.appendChild(loading);

  // ===== BUTTON BELOW GRID =====
  const button = document.createElement('button');
  button.textContent = 'Enviar Itens Selecionados';
  button.style.display = 'block';
  button.style.margin = '24px auto 0 auto';
  button.style.padding = '10px 32px';
  button.style.fontSize = '18px';
  button.style.background = '#1e9cff';
  button.style.color = '#fff';
  button.style.border = 'none';
  button.style.borderRadius = '8px';
  button.style.cursor = 'pointer';
  button.style.boxShadow = '0 2px 12px #0002, 0 0 0 1px #77f07f77';

  button.onclick = async function() {
    const selected = Array.from(document.querySelectorAll('.craft_item_element.selected'))
      .map(el => el.dataset.serverId)
      .filter(id => id && id.length > 0);

    if (!selected.length) return alert('Selecione pelo menos um item!');
    if (!confirm('Deseja enviar TODOS os itens selecionados?')) return;

    button.disabled = true;
    loading.style.display = "flex";
    let ok = 0, fail = 0;

    for (let i = 0; i < selected.length; i++) {
      const url = `https://godswar.online/gw_warehouse?to=web&server_id=${selected[i]}`;
      try {
        let resp = await fetch(url, { credentials: 'include' });
        if (resp.ok) ok++;
        else fail++;
      } catch (e) {
        fail++;
      }
    }
    loading.style.display = "none";
    button.disabled = false;
    alert(`Enviado! Sucesso: ${ok}, Falhas: ${fail}`);
    window.location.reload();
  };

  grid.parentNode.insertBefore(button, grid.nextSibling);

  console.log('Grid por clique sem checkbox visível, hover suave com tooltip abaixo!');
})();
