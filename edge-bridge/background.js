// 小林工具箱 · BOSS 海投记录助手 - 后台桥接
// content script 不能直接跨域请求 localhost，统一由这里发请求（MV3 host_permissions 授权）

const DEFAULT_TOKEN = 'job3-bridge-local-2026';
const API_BASE = 'http://localhost:8000/api/bridge';

async function getToken() {
  const data = await chrome.storage.local.get({ bridgeToken: '' });
  return data.bridgeToken || DEFAULT_TOKEN;
}

async function bridgeFetch(path, options) {
  const token = await getToken();
  const headers = Object.assign({ 'X-Bridge-Token': token }, (options && options.headers) || {});
  const resp = await fetch(API_BASE + path, Object.assign({}, options, { headers }));
  const text = await resp.text();
  let body = null;
  try {
    body = text ? JSON.parse(text) : null;
  } catch (err) {
    body = { raw: text };
  }
  if (!resp.ok) {
    const detail = body && (body.detail || body.message);
    const err = new Error(detail || ('服务返回 HTTP ' + resp.status));
    err.status = resp.status;
    throw err;
  }
  return body;
}

function handleMessage(msg) {
  switch (msg.type) {
    case 'BRIDGE_HEALTH':
      return bridgeFetch('/health');
    case 'BRIDGE_LIST_RESUMES':
      return bridgeFetch('/resumes');
    case 'BRIDGE_LIST_RECORDS':
      return bridgeFetch('/records?limit=5');
    case 'BRIDGE_RECORD_JOB':
      return bridgeFetch('/job-record', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(msg.payload || {})
      });
    case 'BRIDGE_DELETE_RECORD':
      return bridgeFetch('/records/' + encodeURIComponent((msg.payload || {}).snapshotId), { method: 'DELETE' });
    case 'BRIDGE_GET_TOKEN':
      return getToken();
    default:
      return null;
  }
}

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  const promise = msg && handleMessage(msg);
  if (!promise) {
    return false;
  }
  promise
    .then((data) => sendResponse({ ok: true, data: data }))
    .catch((err) => sendResponse({ ok: false, error: String((err && err.message) || err) }));
  return true; // 异步响应
});