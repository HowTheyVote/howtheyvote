<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class AddDeleteCascadeToVoteIdColumnOnMemberVoteTable extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::table('member_vote', function (Blueprint $table) {
            $table->dropForeign(['vote_id']);
            $table->foreign('vote_id')->references('id')->on('votes')->onDelete('cascade');
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::table('member_vote', function (Blueprint $table) {
            //
        });
    }
}
