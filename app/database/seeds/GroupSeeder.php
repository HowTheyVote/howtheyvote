<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;

class GroupSeeder extends Seeder
{
    const GROUPS = [
        'EPP',
        'NI',
        'ID',
        'SD',
        'ECR',
        'GREENS',
        'RENEW',
        'GUE',
        'EFDD',
    ];

    /**
     * Run the database seeds.
     *
     * @return void
     */
    public function run()
    {
        foreach (self::GROUPS as $code) {
            DB::table('groups')->insert([
                'code' => $code,
            ]);
        }
    }
}
