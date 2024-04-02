from flask import Flask, render_template, request, send_file, redirect, url_for
import paramiko

app = Flask(__name__)
app.static_folder = '/home/xuyi/morphing/codes/static'

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    file1 = request.files['file1']
    file2 = request.files['file2']
    frames = request.form['quantity']
    output_file = upload_run_download(file1, file2, frames)
    return send_file(output_file, as_attachment=True)

def upload_run_download(file1, file2, frames):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('192.168.100.231', username='xuyi', password='xuyi2024')
    
    sftp = ssh.open_sftp()
    sftp.putfo(file1, '/home/xuyi/morphing/uploads/' + file1.filename)
    sftp.putfo(file2, '/home/xuyi/morphing/uploads/' + file2.filename)
    sftp.close()

    outfilename = f'{file1.filename.split('.')[0]}_{file2.filename.split('.')[0]}_{frames}.{file1.filename.split('.')[1]}'
    _, stdout, _ = ssh.exec_command(f'python /home/xuyi/morphing/codes/run.py /home/xuyi/morphing/uploads/{file1.filename} \
        							/home/xuyi/morphing/uploads/{file2.filename} \
            						/home/xuyi/morphing/downloads/{outfilename} \
                					{frames}')
    stdout.read()
    ssh.close()
    return f'/home/xuyi/morphing/downloads/{outfilename}'

if __name__ == '__main__':
    app.run(debug=True)
