<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class AddIndexes extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::table('members', function (Blueprint $table) {
            // During imports, members are queried by last name or
            // full name, so a single composite index is enough
            $table->index(['last_name_normalized', 'first_name_normalized']);

            $table->index('country');
        });

        Schema::table('votes', function (Blueprint $table) {
            $table->index('date');
        });

        Schema::table('member_vote', function (Blueprint $table) {
            $table->primary(['member_id', 'vote_id']);
        });

        Schema::table('group_memberships', function (Blueprint $table) {
            // During imports, group memberships are fetched for a known
            // term and start/end date
            $table->index(['term_id', 'start_date', 'end_date']);
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
