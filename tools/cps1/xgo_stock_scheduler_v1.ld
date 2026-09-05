SECTIONS
{
  . = 0x8035eee8;
  .main_sched : { *(.main_sched) }

  . = 0x8035f070;
  .early_sched : { *(.early_sched) }
}
