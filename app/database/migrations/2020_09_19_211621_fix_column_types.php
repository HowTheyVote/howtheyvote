<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class FixColumnTypes extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::table('documents', function (Blueprint $table) {
            $table->integer('number')->change();
        });

        Schema::table('votes', function (Blueprint $table) {
            $table->integer('doceo_vote_id')->change();
            $table->text('description')->change();
        });

        Schema::table('member_vote', function (Blueprint $table) {
            $table->unsignedSmallInteger('position')->change();
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
