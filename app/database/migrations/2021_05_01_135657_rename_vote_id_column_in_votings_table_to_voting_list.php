<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class RenameVoteIdColumnInVotingsTableToVotingList extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::dropIfExists('votings');

        Schema::create('votings', function (Blueprint $table) {
            $table->primary(['voting_list_id', 'member_id']);
            $table->foreignId('voting_list_id')->constrained()->onDelete('cascade');
            $table->foreignId('member_id')->constrained();
            $table->unsignedSmallInteger('position');
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
