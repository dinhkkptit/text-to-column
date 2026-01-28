# Auto platform folders + mapping.json (v14)

## Folder layout (your request)
Put text files under:
- `samples_txt/cisco_ios/*.txt`
- `samples_txt/netscaler_adc/*.txt`
- etc.

Example:
```
samples_txt/
  cisco_ios/
    ciscol21_show_cdp_neighbors.txt
  netscaler_adc/
    netscaler1_show_lb_vserver.txt
```

## mapping.json
Mapping is per **resolved platform**:
```json
{
  "cisco_ios": { "show cdp neighbors": "cisco_ios_show_cdp_neighbors.textfsm", "ping": "cisco_ios_ping.textfsm" },
  "citrix_adc": { "show lb vserver": "...", "show servicegroup": "..." }
}
```

## config.json (platform aliases)
Because folder names may differ from mapping platform keys:
```json
{
  "platform_aliases": {
    "netscaler_adc": "citrix_adc"
  }
}
```

## Run
Parse ALL platform folders automatically:
```powershell
python parse_to_csv.py
```

Parse only one platform folder:
```powershell
python parse_to_csv.py --platform cisco_ios
```

## Output
Writes per-command CSVs into `output/` with prefix `{platform}_`:
- `cisco_ios_show_cdp_neighbors.csv`
- `citrix_adc_show_lb_vserver.csv`
