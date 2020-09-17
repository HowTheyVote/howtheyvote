<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;
use Illuminate\Support\Str;

class NormalizeMembersTable extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::table('members', function (Blueprint $table) {
            $table->string('first_name_lower')->nullable();
            $table->string('last_name_lower')->nullable();
        });

        DB::table('members')->orderBy('id')->each(function ($member) {
            DB::table('members')->where('id', $member->id)->update([
                'first_name_lower' => Str::lower($member->first_name),
                'last_name_lower' => Str::lower($member->last_name),
            ]);
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        //
    }
}
