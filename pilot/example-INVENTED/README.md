# INVENTED example data — not from any utility

Every value in this folder is made up. It shows the **format** we ask a utility for (see
`../../PILOT-READINESS.md`). It contains 2 days of 15-minute readings, with:
- an inlet meter in L/s;
- an outlet meter reported as a cumulative total;
- a gap, an estimated reading and a faulty reading;
- one supply interruption;
- a repair record whose first report, confirmation and repair times all differ.

Convert and check it with:

    python3 ../convert_utility_data.py . ../example-INVENTED-output
