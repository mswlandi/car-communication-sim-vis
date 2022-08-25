import process from 'process'
import buffer from 'buffer'

window.Buffer = buffer.Buffer;
window.process = process;

export {};