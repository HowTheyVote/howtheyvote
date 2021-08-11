<?php

namespace Database\Factories;

use App\Enums\LocationEnum;
use App\Session;
use Illuminate\Database\Eloquent\Factories\Factory;

class SessionFactory extends Factory
{
    /**
     * The name of the factory's corresponding model.
     *
     * @var string
     */
    protected $model = Session::class;

    /**
     * Define the model's default state.
     *
     * @return array
     */
    public function definition()
    {
        return [
            'start_date' =>'2021-08-08',
            'end_date' =>'2021-08-11',
            'location' => LocationEnum::BRUSSELS(),
        ];
    }
}
