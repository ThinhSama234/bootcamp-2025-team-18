
export default interface OutputStream {
  write(payload: string): void;

  setColor(color: string): OutputStream;
}