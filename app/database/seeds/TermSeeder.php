<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;

class TermSeeder extends Seeder
{
    const TERMS = [9];

    /**
     * Run the database seeds.
     *
     * @return void
     */
    public function run()
    {
        foreach (self::TERMS as $number) {
            DB::table('terms')->insert([
                'number' => $number,
            ]);
        }
    }
}
