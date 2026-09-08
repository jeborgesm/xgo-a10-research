# Test08 hardware result — full console scanner PASS

Date: 2026-09-07
Branch: `research-game-list-general-scanner`

Status: **HARDWARE PASS**

## Result

The Test08 table-driven built-in console scanner was tested on the disposable XGO card and successfully discovered previously unindexed games in multiple built-in system directories.

This closes the central discovery/stable-merge proof:

```text
Refresh
 -> scan real filesystem
 -> classify ROMs
 -> compare against existing built-in catalogs
 -> append missing entries
 -> expose them in the stock main lists
 -> launch through the normal emulator path
```

The candidate package contained no staged catalog data, no `Resources/refresh.bin`, and no test ROM payload, so the newly exposed entries necessarily came from runtime filesystem discovery.

## Observed hardware evidence

### FC / Famicom

Refresh discovered at least:

- `Bomberman 2`
- `Home Alone`

`Home Alone` launched and played correctly.

`Bomberman 2` was exposed by the scanner but still does not run. This is an emulator/game compatibility issue rather than a discovery failure: the scanner successfully indexed and exposed the physical game.

### GB / Game Boy

A particularly strong unplanned proof occurred in the GB directory.

The card still contained ordinary raw `.gb` files that had been manually added when the device was first obtained as an experiment to see whether the stock frontend would discover them. They had remained invisible in the stock main list and had been forgotten.

Test08 discovered those old raw `.gb` files automatically and added them to the normal Game Boy list.

Observed example:

`Super Mario Land (W) (V1.1) [!].gb`

The game:
- appeared in the stock GB main list after Refresh;
- launched successfully as a raw `.gb` ROM;
- played normally;
- accepted the existing XGO button-remapping mechanism;
- remained playable with the remapped controls.

This independently validates both native-extension classification and the stock launch path for newly indexed raw ROMs. The discovery was not tailored to a known test filename.

The captured Windows directory view also shows raw `.gb` files coexisting with the stock `.zgb` wrappers in `/GB`, including Super Mario Land and other manually added titles.

## Box-art observation

Newly discovered raw GB games do not automatically show box art.

This is expected to be a separate metadata/artwork problem from catalog discovery. Test08 currently synthesizes slot-1/title and slot-2/search fallback strings from the filename basename; it does not create or resolve whatever artwork association the stock frontend expects.

Do not treat missing artwork as a Test08 scanner failure.

## Conclusion

Test08 proves the XGO can perform a real, general on-device refresh of built-in console libraries without PC-generated replacement catalogs and without per-ROM hardcoding.

The result is materially stronger than the earlier staged and single-system proofs because:
- multiple system directories changed from one Refresh operation;
- multiple previously unindexed titles were discovered;
- a forgotten raw GB ROM supplied an accidental blind test;
- that raw ROM launched and played normally;
- button remapping continued to work.

## Remaining work

1. Promote the six-console discovery/stable-merge scanner to the protected/golden lineage after preserving the exact hardware-tested artifact.
2. Add transaction marker + backup/recovery so interruption during the three-file canonical rewrite cannot leave a catalog triplet inconsistent.
3. Investigate stock box-art lookup/association for newly discovered games.
4. Investigate Arcade wrapper-family classification before extending the general scanner to the shared `ARCADE` directory.
5. Keep emulator compatibility failures such as Bomberman 2 separate from scanner correctness.
