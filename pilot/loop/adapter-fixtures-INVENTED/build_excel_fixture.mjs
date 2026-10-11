// Every date, meter, reading and quality code in this workbook is INVENTED.
// The formula and merged-header sheets are intentionally rejected test inputs.
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const outputDir = path.dirname(fileURLToPath(import.meta.url));
const book = Workbook.create();
const minutes = [0, 15, 30, 45, 90, 105];
const values1 = [1.25, 2.5, 0, null, 4, 4.5];
const values2 = [2, 2, 0, 1, 3, 3];
const flags1 = ['GOOD', 'GOOD', 'GOOD', 'GOOD', 'FAULT', 'GOOD'];
const flags2 = ['GOOD', 'GOOD', 'EST', 'GOOD', 'GOOD', 'GOOD'];
const iso = m => `2026-01-01T${String(Math.floor(m / 60)).padStart(2, '0')}:${String(m % 60).padStart(2, '0')}:00+02:00`;
// Explicit Excel-1900 serials keep UTC wall time stable in this fixture writer.
// The dates are all modern: the historical 1900 leap-day anomaly is irrelevant.
const excelEpoch = Date.UTC(1899, 11, 30);
const utcTime = m => (Date.parse(iso(m)) - excelEpoch) / 86400000;
const wideHeaders = ['Time', 'INVENTED-M1 flow', 'INVENTED-M1 flag', 'INVENTED-M2 flow', 'INVENTED-M2 flag'];

function sheet(name, headers, rows, note) {
  const sh = book.worksheets.add(name);
  sh.showGridLines = false;
  sh.getRange('A1').values = [['All readings and dates are INVENTED']];
  sh.getRange('A2').values = [[note]];
  sh.getRange('A3:E3').values = [headers];
  sh.getRange(`A4:E${rows.length + 3}`).setNumberFormat('@');
  sh.getRange(`A4:E${rows.length + 3}`).values = rows;
  sh.getRange(`A1:E${rows.length + 3}`).format.font = {name: 'Arial', size: 11, color: '#202124'};
  sh.getRange('A1').format.font = {name: 'Arial', size: 14, bold: true};
  sh.getRange('A3:E3').format = {fill: '#334155', font: {name: 'Arial', size: 11, bold: true, color: '#FFFFFF'}, horizontalAlignment: 'center'};
  sh.getRange(`A1:E${rows.length + 3}`).format.rowHeight = 23;
  sh.getRange('A1:E2').format.rowHeight = 27;
  sh.getRange(`A1:E${rows.length + 3}`).format.verticalAlignment = 'center';
  sh.getRange('A1:E2').format.wrapText = false;
  sh.getRange(`A3:E${rows.length + 3}`).format.columnWidth = 23;
  sh.getRange(`A3:A${rows.length + 3}`).format.columnWidth = 47;
  return sh;
}

const longRows = minutes.flatMap((m, i) => [
  ['INVENTED-M1', utcTime(m), values1[i], 'L/s', flags1[i]],
  ['INVENTED-M2', utcTime(m), values2[i], 'm3/h', flags2[i]]
]);
const long = sheet('INVENTED_Long', ['Meter', 'Time', 'Reading', 'Units', 'Status'], longRows,
                   'Time is UTC. Blank means missing. Zero is a recorded zero.');
long.getRange('A3:A15').format.columnWidth = 23;
long.getRange('B3:B15').format.columnWidth = 47;
long.getRange('B4:B15').setNumberFormat('yyyy-mm-dd hh:mm:ss');
long.getRange('C4:C15').setNumberFormat('0.00');

const wideRows = minutes.map((m, i) => [utcTime(m), values1[i], flags1[i], values2[i], flags2[i]]);
const wide = sheet('INVENTED_Wide', wideHeaders, wideRows,
                   'Time is UTC. Same invented readings, one column per meter.');
wide.getRange('B4:B9').setNumberFormat('0.00');
wide.getRange('D4:D9').setNumberFormat('0.00');
wide.getRange('A4:A9').setNumberFormat('yyyy-mm-dd hh:mm:ss');

const nativeRows = minutes.map((m, i) => [new Date(Date.UTC(2026, 0, 1, 0, m)), values1[i], flags1[i], values2[i], flags2[i]]);
const native = sheet('INVENTED_NativeDates', wideHeaders, nativeRows,
                     'Excel dates have no timezone. Tests explicitly declare UTC+02:00.');
native.getRange('A4:A9').setNumberFormat('yyyy-mm-dd hh:mm:ss');
native.getRange('B4:B9').setNumberFormat('0.00');
native.getRange('D4:D9').setNumberFormat('0.00');

const formula = sheet('INVENTED_Formula', wideHeaders, wideRows,
                      'B4 is deliberately calculated. The adapter must reject it.');
formula.getRange('A4:A9').setNumberFormat('yyyy-mm-dd hh:mm:ss');
formula.getRange('B4').formulas = [['=1+1']];

const merged = sheet('INVENTED_Merged', ['Time', 'Combined field', null, 'INVENTED-M2 flow', 'INVENTED-M2 flag'],
                     wideRows, 'The merged header is deliberately unsupported.');
merged.getRange('A4:A9').setNumberFormat('yyyy-mm-dd hh:mm:ss');
merged.mergeCells('B3:C3');

book.recalculate();
const inspected = await book.inspect({kind: 'table', range: 'INVENTED_Long!A3:E7', include: 'values,formulas', tableMaxRows: 5, tableMaxCols: 5, maxChars: 2000});
console.log(inspected.ndjson);
const scan = await book.inspect({kind: 'match', searchTerm: '#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!', options: {useRegex: true, maxResults: 10}, maxChars: 1000});
console.log(scan.ndjson);
for (const name of ['INVENTED_Long', 'INVENTED_Wide', 'INVENTED_NativeDates', 'INVENTED_Formula', 'INVENTED_Merged']) {
  if (name === 'INVENTED_NativeDates' && process.argv.includes('--skip-native-preview')) continue;
  const preview = await book.render({sheetName: name, range: name === 'INVENTED_Long' ? 'A1:E15' : 'A1:E9', scale: 1, format: 'png'});
  await fs.writeFile(path.join(outputDir, `${name}.png`), new Uint8Array(await preview.arrayBuffer()));
}
const file = await SpreadsheetFile.exportXlsx(book);
await file.save(path.join(outputDir, 'exports-INVENTED.xlsx'));
console.log('Saved one INVENTED workbook with five distinct adapter test layouts.');
