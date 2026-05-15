import fs from "node:fs";
import path from "node:path";

export class JsonStore<T> {
  constructor(private filePath: string, private fallback: T) {}

  read(): T {
    if (!fs.existsSync(this.filePath)) return this.fallback;
    try {
      return JSON.parse(fs.readFileSync(this.filePath, "utf8")) as T;
    } catch {
      return this.fallback;
    }
  }

  write(data: T) {
    fs.mkdirSync(path.dirname(this.filePath), { recursive: true });
    fs.writeFileSync(this.filePath, JSON.stringify(data, null, 2), "utf8");
  }
}
