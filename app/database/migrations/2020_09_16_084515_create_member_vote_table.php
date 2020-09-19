<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class CreateMemberVoteTable extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::create('member_vote', function (Blueprint $table) {
            $table->foreignId('member_id')->constrained();
            $table->foreignId('vote_id')->constrained();
            $table->string('position', 16);

            $table->unique(['member_id', 'vote_id']);
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::dropIfExists('member_vote');
    }
}
