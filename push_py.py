import subprocess
import os

os.chdir(r'D:\data_1m\tdx_futures_data')

# Set git to not use proxy
result = subprocess.run(['git', 'config', '--global', '--add', 'safe.directory', r'D:\data_1m\tdx_futures_data'], capture_output=True)
result = subprocess.run(['git', 'remote', 'set-url', 'origin', 'https://github.com/quantiger/tdx-futures-data.git'], capture_output=True)
result = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True)
print("Remote:", result.stdout, result.stderr)

# Push with explicit no proxy
env = os.environ.copy()
env['GIT_SSH_COMMAND'] = 'ssh -o StrictHostKeyChecking=no'
result = subprocess.run(['git', 'push', '-u', 'origin', 'master'], capture_output=True, text=True, env=env)
print("Push:", result.stdout, result.stderr)