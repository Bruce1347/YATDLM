import subprocess

def main():
    # Run migrations
    migrations = subprocess.run(["python3", "./manage.py", "migrate"])

if __name__ == '__main__':
    main()