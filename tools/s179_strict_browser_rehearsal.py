from pathlib import Path
import argparse
import sys,json,threading,subprocess,time,tempfile,hashlib
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'src'))
from culinarystate.app.strict_server_v3 import make_server
from culinarystate.decision.demo_context_v3 import StrictDemoContext
parser=argparse.ArgumentParser(description='Isolated local Chrome technical rehearsal; not a human presentation event.')
parser.add_argument('--out',type=Path,required=True)
parser.add_argument('--screenshot',type=Path,required=True)
args=parser.parse_args()
if args.out.exists() or args.screenshot.exists():parser.error('Refusing to overwrite rehearsal outputs')
started=datetime.now(timezone.utc).isoformat();ctx=StrictDemoContext.load(public=True,host='127.0.0.1')
server=make_server(('127.0.0.1',0),ctx,per_minute=100)
thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
profile=Path(tempfile.mkdtemp(prefix='culinarystate-strict-v3-browser-'))
chrome='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
log=open('/private/tmp/strict-v3-chrome.log','wb')
proc=subprocess.Popen([chrome,'--headless','--disable-gpu','--disable-background-networking','--no-first-run','--no-default-browser-check','--remote-debugging-port=0','--user-data-dir='+str(profile),'about:blank'],stdout=log,stderr=log)
try:
 for _ in range(200):
  if (profile/'DevToolsActivePort').exists() and (profile/'DevToolsActivePort').read_text().strip():break
  if proc.poll() is not None:raise RuntimeError('Chrome exited')
  time.sleep(.05)
 port=(profile/'DevToolsActivePort').read_text().splitlines()[0]
 screenshot=args.screenshot.resolve()
 subprocess.run(['/opt/homebrew/bin/node',str(root/'tools/s179_strict_browser_driver.mjs'),port,f'http://127.0.0.1:{server.server_port}','/private/tmp/strict-v3-browser-results.json',str(screenshot)],check=True,timeout=60)
 result=json.loads(Path('/private/tmp/strict-v3-browser-results.json').read_text())
 result.update(record='STRICT_V3_ISOLATED_BROWSER_TECHNICAL_REHEARSAL',started_at_utc=started,completed_at_utc=datetime.now(timezone.utc).isoformat(),labels=['ENGINEERING_DIAGNOSTIC','NON_CITABLE','NO_HUMAN_SIGNOFF_D085'],scientific_gate_pass=False,claim_24_nov_rehearsal=False,screenshot={'path':str(screenshot.relative_to(root)),'sha256':hashlib.sha256(screenshot.read_bytes()).hexdigest()},driver_sha256=hashlib.sha256((root/'tools/s179_strict_browser_driver.mjs').read_bytes()).hexdigest(),limitations=['Four scripted local synthetic UI cases and a planted missing-value control; not natural-query validation.','Local public-filtered mode only; original frozen scientific results are unchanged.','Technical rehearsal on12Nov is not the required24Nov timed human presentation event.','Screenshot is static fallback from synthetic caller input, not experimental evidence.'])
 out=args.out
 with out.open('x') as f:f.write(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps(result))
finally:
 proc.terminate()
 try:proc.wait(timeout=10)
 except subprocess.TimeoutExpired:proc.kill();proc.wait()
 server.shutdown();server.server_close();thread.join();log.close()
