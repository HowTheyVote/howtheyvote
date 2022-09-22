<?php

namespace App\Enums;

enum CountryEnum: string
{
    case AT = 'AT';
    case BE = 'BE';
    case BG = 'BG';
    case CY = 'CY';
    case CZ = 'CZ';
    case DE = 'DE';
    case DK = 'DK';
    case EE = 'EE';
    case ES = 'ES';
    case FI = 'FI';
    case FR = 'FR';
    case GB = 'GB';
    case GR = 'GR';
    case HR = 'HR';
    case HU = 'HU';
    case IE = 'IE';
    case IT = 'IT';
    case LT = 'LT';
    case LU = 'LU';
    case LV = 'LV';
    case MT = 'MT';
    case NL = 'NL';
    case PL = 'PL';
    case PT = 'PT';
    case RO = 'RO';
    case SE = 'SE';
    case SI = 'SI';
    case SK = 'SK';

    public function label(): string
    {
        return match ($this) {
            self::AT => 'Austria',
            self::BE => 'Belgium',
            self::BG => 'Bulgaria',
            self::CY => 'Cyprus',
            self::CZ => 'Czech Republic',
            self::DE => 'Germany',
            self::DK => 'Denmark',
            self::EE => 'Estonia',
            self::ES => 'Spain',
            self::FI => 'Finland',
            self::FR => 'France',
            self::GB => 'United Kingdom',
            self::GR => 'Greece',
            self::HR => 'Croatia',
            self::HU => 'Hungary',
            self::IE => 'Ireland',
            self::IT => 'Italy',
            self::LT => 'Lithuania',
            self::LU => 'Luxembourg',
            self::LV => 'Latvia',
            self::MT => 'Malta',
            self::NL => 'Netherlands',
            self::PL => 'Poland',
            self::PT => 'Portugal',
            self::RO => 'Romania',
            self::SE => 'Sweden',
            self::SI => 'Slovenia',
            self::SK => 'Slovakia',
        };
    }

    public function emoji(): string
    {
        return match ($this) {
            self::AT => '🇦🇹',
            self::BE => '🇧🇪',
            self::BG => '🇧🇬',
            self::CY => '🇨🇾',
            self::CZ => '🇨🇿',
            self::DE => '🇩🇪',
            self::DK => '🇩🇰',
            self::EE => '🇪🇪',
            self::ES => '🇪🇸',
            self::FI => '🇫🇮',
            self::FR => '🇫🇷',
            self::GB => '🇬🇧',
            self::GR => '🇬🇷',
            self::HR => '🇭🇷',
            self::HU => '🇭🇺',
            self::IE => '🇮🇪',
            self::IT => '🇮🇹',
            self::LT => '🇱🇻',
            self::LU => '🇱🇺',
            self::LV => '🇱🇹',
            self::MT => '🇲🇹',
            self::NL => '🇳🇱',
            self::PL => '🇵🇱',
            self::PT => '🇵🇹',
            self::RO => '🇷🇴',
            self::SE => '🇸🇪',
            self::SI => '🇸🇮',
            self::SK => '🇸🇰',
        };
    }

    public static function make(string $country): static
    {
        return match ($country) {
            'AT' => static::AT,
            'BE' => static::BE,
            'BG' => static::BG,
            'CY' => static::CY,
            'CZ' => static::CZ,
            'DE' => static::DE,
            'DK' => static::DK,
            'EE' => static::EE,
            'ES' => static::ES,
            'FI' => static::FI,
            'FR' => static::FR,
            'GB' => static::GB,
            'GR' => static::GR,
            'HR' => static::HR,
            'HU' => static::HU,
            'IE' => static::IE,
            'IT' => static::IT,
            'LT' => static::LT,
            'LU' => static::LU,
            'LV' => static::LV,
            'MT' => static::MT,
            'NL' => static::NL,
            'PL' => static::PL,
            'PT' => static::PT,
            'RO' => static::RO,
            'SE' => static::SE,
            'SI' => static::SI,
            'SK' => static::SK,
        };
    }

    public static function toValues()
    {
        return array_map(
            fn (CountryEnum $c) => $c->name,
            CountryEnum::cases());
    }
}
