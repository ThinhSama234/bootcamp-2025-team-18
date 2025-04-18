import OutputStream from "./OutputStream";

export default class ConsoleOutputStream implements OutputStream {
  write(payload: string): void {
    console.log(this._color + payload);
  }

  setColor(color: string): OutputStream {
    this._color = color;
    return this;
  }

  private _color: string = 'color:white;';
}