// 小林工具箱 · BOSS 海投记录助手 - 弹窗
(function () {
  var statusEl = document.getElementById('status');
  var tokenEl = document.getElementById('token');
  var saveMsg = document.getElementById('save-msg');

  function bridge(type, payload) {
    return new Promise(function (resolve) {
      chrome.runtime.sendMessage({ type: type, payload: payload }, function (resp) {
        if (chrome.runtime.lastError) {
          resolve({ ok: false, error: chrome.runtime.lastError.message });
          return;
        }
        resolve(resp || { ok: false, error: '无响应' });
      });
    });
  }

  function setStatus(text, cls) {
    statusEl.textContent = text;
    statusEl.className = 'status' + (cls ? ' ' + cls : '');
  }

  function check() {
    setStatus('正在检测本地服务…');
    bridge('BRIDGE_HEALTH').then(function (r) {
      if (r.ok) {
        var v = (r.data && r.data.version) || '';
        setStatus('✅ 本地服务已连接' + (v ? '（工具箱 v' + v + '）' : '') + '，可以开始记录。', 'ok');
      } else {
        setStatus('❌ 无法连接：' + r.error + '\n请先启动后端服务（http://localhost:8000）。', 'err');
      }
    });
  }

  chrome.storage.local.get({ bridgeToken: '' }, function (data) {
    tokenEl.value = data.bridgeToken || '';
  });

  document.getElementById('save').addEventListener('click', function () {
    var v = tokenEl.value.trim();
    if (!v) {
      saveMsg.textContent = 'Token 不能为空';
      return;
    }
    chrome.storage.local.set({ bridgeToken: v }, function () {
      saveMsg.textContent = '✅ 已保存，之后所有请求将携带该 Token。';
      setTimeout(function () { saveMsg.textContent = ''; }, 2500);
      check();
    });
  });

  document.getElementById('check').addEventListener('click', check);
  check();
})();