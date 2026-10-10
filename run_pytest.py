import subprocess

def main():
    exe = r'c:/Users/ASHISH S YADAV.LAPTOP-LEK06VOJ/OneDrive/Desktop/kanishka/.venv-1/Scripts/python.exe'
    proc = subprocess.run(
        [exe, '-m', 'pytest', '-q'],
        cwd=r'c:/Users/ASHISH S YADAV.LAPTOP-LEK06VOJ/OneDrive/Desktop/kanishka',
        capture_output=True,
        text=True,
    )
    with open('pytest_out.txt', 'w', encoding='utf-8') as f:
        f.write(proc.stdout)
        f.write('\n---STDERR---\n')
        f.write(proc.stderr)
        f.write(f'\nEXIT={proc.returncode}\n')

if __name__ == '__main__':
    main()
