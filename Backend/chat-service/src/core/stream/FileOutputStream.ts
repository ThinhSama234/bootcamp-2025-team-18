import OutputStream from "./OutputStream";
import fs from 'fs';


export default class FileOutputStream implements OutputStream {
  constructor(path: string) {
    this._path = path;
    const dir = path.substring(0, path.lastIndexOf('/'));
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    if (!fs.existsSync(this._path)) {
      fs.writeFileSync(this._path, '', 'utf8');
    }
  }

  write(payload: string): void {
    payload += '\n';
    fs.appendFile(this._path, payload, 'utf8', err => {
      if (err)
        console.error('Error writing to file: ', err);
    })
  }

  setColor(_color: string): OutputStream {
    return this;
  }

  private _path: string;
}